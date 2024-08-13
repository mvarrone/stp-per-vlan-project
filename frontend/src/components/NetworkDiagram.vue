<template>
    <div>
        <div class="offcanvas offcanvas-end" tabindex="-1" id="offcanvasRight" aria-labelledby="offcanvasRightLabel">
            <div class="offcanvas-header">
                <div class="header-content">
                    <img :src="`./src/components/icons/${selectedNodeDeviceType}.png`" alt="Icon" class="sidebar-icon">
                    <h5 class="offcanvas-title" id="offcanvasRightLabel">{{ sidebarTitle }}</h5>
                </div>
                <button type="button" class="btn-close" data-bs-dismiss="offcanvas" aria-label="Close"></button>
            </div>
            <div class="offcanvas-body">
                <div v-if="selectedElementType === 'node'">
                    <p><strong>SVI:</strong> {{ selectedNodeDevice }}</p>
                    <p><strong>Platform:</strong> {{ selectedNodeDeviceType }}</p>
                    <p><strong>Level:</strong> {{ selectedNodeLevel }}</p>
                    <p><strong>Priority:</strong> {{ selectedNodePriority }}</p>
                    <p><strong>MAC Address:</strong> {{ selectedNodeMACAddress }}</p>
                    <p><strong>Cost to Root Bridge:</strong> {{ selectedNodeCost }}</p>
                    <p><strong>Version:</strong> {{ selectedNodeVersion }}</p>
                    <p><strong>Uptime:</strong> {{ selectedNodeUptime }}</p>
                    <p><strong>Serial:</strong> {{ selectedNodeSerial }}</p>
                    <div>
                        <p><strong>Blocked interface(s): {{ blockedInterfacesCount }}</strong></p>
                        <ul v-if="hasBlockedInterfaces">
                            <li v-for="(intf, index) in currentDeviceBlockedInterfaces" :key="index">
                                {{ intf }}
                            </li>
                        </ul>
                    </div>
                </div>
                <div v-else-if="selectedElementType === 'edge'">
                    <!-- <p><strong>From:</strong> {{ selectedEdgeFrom }}</p>
                    <p><strong>To:</strong> {{ selectedEdgeTo }}</p>
                    <p><strong>Title:</strong> {{ selectedEdgeTitle }}</p> -->
                    <p>{{ selectedEdgeTitle }}</p>
                </div>
                <div v-if="selectedElementType === 'info_blocked_links'">
                <p><strong>Number of devices with blocked interfaces: {{ blocked_interfaces.length }}</strong></p>
                <p><strong>Number of blocked interfaces: {{ totalBlockedInterfaces }}</strong></p>
                <ul>
                    <li v-for="(item, index) in blocked_interfaces" :key="index">
                        <strong>{{ Object.keys(item)[0] }}</strong>
                        <ul>
                            <li v-for="(intf, interfaceIndex) in item[Object.keys(item)[0]].interfaces" :key="interfaceIndex">
                                {{ intf }}
                            </li>
                        </ul>
                    </li>
                </ul>
            </div>
            </div>
        </div>
        <div v-if="isLoading" class="loading-container">
            <div class="loading-message">
                <span class="loading-spinner"></span>
                Loading...
            </div>
        </div>
        <div v-else>
            <div v-if="errorMessage" class="error-message">
                {{ errorMessage }}
            </div>
            <div v-else>
                <div class="checkbox-container">
                    <div class="left-controls">
                        <label>
                            <input type="checkbox" v-model="useFilteredEdges" @change="toggleEdges">
                            Show blocked links
                        </label>
                    </div>

                    <div class="vlan-dropdown-container">
                        <label for="vlan-select">Logical topology for</label>
                        <select id="vlan-select" v-model="selectedVlan" @change="handleVlanChange">
                            <option v-for="vlan in dataPerVlan" :key="vlan.vlan_id" :value="vlan.vlan_id">
                                VLAN {{ vlan.vlan_id }}
                            </option>
                        </select>
                    </div>

                    <div class="right-controls">
                        <label>
                            <input type="checkbox" v-model="checked" @change="infoBlockedLinks">
                            Show blocked link information
                        </label>
                        <span class="elapsed-time">Processing time: {{ elapsed_time.amount }} {{ elapsed_time.unit }}</span>
                    </div>
                </div>
                <div id="mynetwork"></div>
            </div>
        </div>
    </div>
</template>

<script>
import axios from "axios";
import { Network } from 'vis-network';
import 'bootstrap/dist/css/bootstrap.min.css';
import 'bootstrap';

export default {
    name: "NetworkDiagram",
    data() {
        return {
            nodes: [],
            edges: [],
            edges_with_blocked_links: [],
            blocked_interfaces: [],
            results: [],
            isLoading: false,
            errorMessage: '',
            useFilteredEdges: false,
            network: null,
            elapsed_time: 0,
            sidebarTitle: '',
            selectedNodeDevice: '',
            selectedNodeDeviceType: '',
            selectedNodeLevel: '',
            selectedNodePriority: '',
            selectedNodeMACAddress: '',
            selectedNodeCost: -1,
            selectedNodeVersion: '',
            selectedNodeUptime: '',
            selectedNodeSerial: '',
            selectedElementType: '',
            selectedEdgeFrom: '',
            selectedEdgeTo: '',
            selectedEdgeTitle: '',
            checked: false,
            offcanvas: null,
            selectedVlan: 0,
            dataPerVlan: []
        }
    },
    mounted() {
        this.getNodesAndEdges()
            .then(() => {
                this.initNetwork();
                this.initOffcanvas();
            })
            .catch(err => {
                console.log(err);
            });
    },
    computed: {
        totalBlockedInterfaces() {
            return this.blocked_interfaces.reduce((total, item) => {
                const deviceKey = Object.keys(item)[0];
                return total + item[deviceKey].interfaces.length;
            }, 0);
        },
        hasBlockedInterfaces() {
            return this.blockedInterfacesCount > 0;
        },
        currentDeviceBlockedInterfaces() {
            const device = this.blocked_interfaces.find(d => Object.keys(d)[0] === this.sidebarTitle);
            return device ? device[this.sidebarTitle].interfaces : [];
        },
        blockedInterfacesCount() {
            return this.currentDeviceBlockedInterfaces.length;
        }
    },
    methods: {
        handleVlanChange() {
            console.log("Selected VLAN ID in dropdown:", this.selectedVlan);

            const vlanId = parseInt(this.selectedVlan, 10);
            const vlanData = this.dataPerVlan.find(vlan => vlan.vlan_id === vlanId);
            console.log("vlanData:", vlanData);

            if (vlanData) {
                this.nodes = vlanData.nodes;
                this.edges = vlanData.edges;
                this.edges_with_blocked_links = vlanData.edges_with_blocked_links;
                this.blocked_interfaces = vlanData.blocked_interfaces;
                this.results = vlanData.results;
                //this.vlan_id = vlanData.vlan_id;
            } else {
                console.error(`VLAN with ID ${vlanId} not found`);
            }

            this.initNetwork();
            this.initOffcanvas();
            this.useFilteredEdges = false; // It fixes a small bug after selecting a new vlan ID option from dropdown
        },
        initOffcanvas() {
            const offcanvasElement = document.getElementById('offcanvasRight');
            this.offcanvas = new bootstrap.Offcanvas(offcanvasElement);
            
            offcanvasElement.addEventListener('hidden.bs.offcanvas', this.handleOffcanvasHidden);
        },
        handleOffcanvasHidden() {
            if (this.selectedElementType === 'info_blocked_links') {
                this.checked = false;
            }
        },
        getNodesAndEdges() {
            this.isLoading = true;
            this.errorMessage = '';
            
            const protocol = import.meta.env.VITE_API_PROTOCOL;
            const host = import.meta.env.VITE_API_HOST;
            const port = import.meta.env.VITE_API_PORT;
            const endpoint = import.meta.env.VITE_API_ENDPOINT_STP_GRAPH;
            const url = `${protocol}://${host}:${port}${endpoint}`;
            
            return axios
                .get(url)
                .then(response => {
                    //console.log("response from API:", response);
                    //console.log("data from API:", response.data);

                    this.dataPerVlan = response.data.data_per_vlan;
                    //console.log("dataPerVlan:", this.dataPerVlan);
                    this.elapsed_time = response.data.elapsed_time;

                    this.selectedVlan = 1; // Set VLAN ID = 1 (Native VLAN) to show after axios response
                    const vlanData = this.dataPerVlan.find(vlan => vlan.vlan_id === this.selectedVlan);
                    if (vlanData) {
                        this.nodes = vlanData.nodes;
                        this.edges = vlanData.edges;
                        this.edges_with_blocked_links = vlanData.edges_with_blocked_links;
                        this.blocked_interfaces = vlanData.blocked_interfaces;
                        this.results = vlanData.results;
                        //this.vlan_id = vlanData.vlan_id;
                    } else {
                        console.error(`VLAN with ID ${selectedVlan} not found`);
                    }
                })
                .catch(error => {
                    this.error_description = error.response.data.detail;
                    this.status_code = error.response.status;
                    this.status_text = error.response.statusText;
                    this.errorMessage = `${this.error_description}. Status code: ${this.status_code} (${this.status_text})`;
                })
                .finally(() => {
                    this.isLoading = false;
                });
        },
        initNetwork() {
            const container = document.getElementById('mynetwork');
            const data = {
                nodes: this.nodes,
                edges: this.edges
            };
            const options = this.getNetworkOptions();
            this.updateNetwork(container, data, options);
        },
        updateNetwork(container, data, options) {
            if (this.network) {
                this.network.destroy();
            }
            this.network = new Network(container, data, options);

            // Save a reference to 'this' for use it within the callback function
            const self = this;

            // onClick event handler
            this.network.on("click", function (params) {
                const selected_node = this.getNodeAt(params.pointer.DOM);
                const selected_edge = this.getEdgeAt(params.pointer.DOM);
                
                if (selected_node != null) {
                    //console.log("Click event. node id: " + selected_node);

                    // Look for the selected node within results variable
                    const selectedNodeResult = self.results.find(result => result.id === selected_node);

                    if (selectedNodeResult) {
                        // Save data to show in sidebar
                        self.sidebarTitle = selectedNodeResult.label;
                        self.selectedElementType = 'node';

                        self.selectedNodeDevice = selectedNodeResult.device;
                        self.selectedNodeDeviceType = selectedNodeResult.device_type;
                        self.selectedNodeLevel = selectedNodeResult.level;
                        self.selectedNodePriority = selectedNodeResult.priority;
                        self.selectedNodeMACAddress = selectedNodeResult.mac_address;
                        self.selectedNodeCost = selectedNodeResult.cost_to_root_bridge;
                        self.selectedNodeVersion = selectedNodeResult.version;
                        self.selectedNodeUptime = selectedNodeResult.uptime;
                        self.selectedNodeSerial = selectedNodeResult.serial;

                        // Show sidebar
                        const offcanvasElement = document.getElementById('offcanvasRight');
                        const offcanvas = new bootstrap.Offcanvas(offcanvasElement);
                        offcanvas.show();

                    } else {
                        console.log("No info found for the selected node");
                        self.selectedNode = null;
                    }
                } else if (selected_edge != null) {     
                    // Look for the selected edge within edges or edges_with_blocked_links
                    let selectedEdgeResult = null;
                    
                    if (self.useFilteredEdges) {
                        selectedEdgeResult = self.edges_with_blocked_links.find(edge => edge.id === selected_edge);
                    } else {
                        selectedEdgeResult = self.edges.find(edge => edge.id === selected_edge);
                    }

                    if (selectedEdgeResult) {
                        // Save data to show in sidebar
                        self.sidebarTitle = 'Link information'
                        self.selectedElementType = 'edge';

                        self.selectedNodeDeviceType = "information"
                        //self.selectedEdgeFrom = selectedEdgeResult.from;
                        //self.selectedEdgeTo = selectedEdgeResult.to;
                        self.selectedEdgeTitle = selectedEdgeResult.title;

                        // Show sidebar
                        const offcanvasElement = document.getElementById('offcanvasRight');
                        const offcanvas = new bootstrap.Offcanvas(offcanvasElement);
                        offcanvas.show();

                    } else {
                        console.log("No info found for the selected edge");
                        self.selectedEdge = null;
                    }
                }
            });
        },
        toggleEdges() {
            const container = document.getElementById('mynetwork');
            const data = {
                nodes: this.nodes,
                edges: this.useFilteredEdges ? this.edges_with_blocked_links : this.edges
            };
            const options = this.getNetworkOptions();

            this.updateNetwork(container, data, options);
        },
        infoBlockedLinks() {
            if (this.checked) {
                this.selectedElementType = 'info_blocked_links';
                this.sidebarTitle = 'Information';
                this.selectedNodeDeviceType = "information";

                this.offcanvas.show();
            } else {
                this.offcanvas.hide();
            }
        },
        beforeUnmount() {
            // Clean up the event listener when the component is destroyed
            const offcanvasElement = document.getElementById('offcanvasRight');
            offcanvasElement.removeEventListener('hidden.bs.offcanvas', this.handleOffcanvasHidden);
        },
        getNetworkOptions() {
            return {
                nodes: {
                    font: {
                        size: 18,
                        color: "#000000"
                    },
                    borderWidth: 1,
                    shadow: true,
                },
                edges: {
                    smooth: {
                        enabled: true,
                        type: "cubicBezier",
                        forceDirection: "vertical",
                        roundness: 0.5
                    }
                },
                interaction: {
                    hover: true,
                    tooltipDelay: 50
                },
                layout: {
                    hierarchical: {
                        direction: "DU",
                        sortMethod: 'directed'
                    }
                },
                physics: {
                    enabled: true,
                    stabilization: false
                }
            };
        }
    },
}
</script>

<style>
    html,
    body {
        height: 100%;
        margin: 0;
        padding: 0;
        background-color: #333;
    }

    #mynetwork {
        width: 100%;
        height: 877px;
        border: 1px solid #333;
        background-color: #333;
    }

    h2 {
        text-align: center;
    }

    .loading-container {
        display: flex;
        justify-content: center;
        align-items: center;
        height: 100vh;
    }

    .loading-message {
        display: flex;
        flex-direction: column;
        align-items: center;
        font-size: 18px;
        color: #fdfdfd;
    }

    .loading-spinner {
        display: inline-block;
        width: 24px;
        height: 24px;
        border-radius: 50%;
        border: 4px solid #ccc;
        border-top-color: #888;
        animation: spin 1s ease-in-out infinite;
        margin-bottom: 8px;
    }

    @keyframes spin {
        0% {
            transform: rotate(0deg);
        }

        100% {
            transform: rotate(360deg);
        }
    }

    .error-message {
        margin: 16px;
        padding: 16px;
        background-color: #ffdddd;
        color: #ff0000;
        border: 1px solid #ff0000;
        border-radius: 4px;
    }

    .vis-tooltip {
        position: absolute;
        visibility: visible;
        background-color: #f9f9f9;
        border: 1px solid #d3d3d3;
        border-radius: 4px;
        padding: 8px;
        box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
        z-index: 10;
    }

    .offcanvas-title {
        font-weight: bold;
    }

    .offcanvas-body p {
        margin: 0;
        padding: 8px 0;
    }

    .offcanvas-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
    }

    .header-content {
        display: flex;
        align-items: center;
    }

    .check-button {
        margin-left: 55px;
    }

    .sidebar-icon {
        width: 24px;
        /* Ajusta el tamaño de la imagen según sea necesario */
        height: 24px;
        margin-right: 10px;
        /* Espacio entre la imagen y el título */
        object-fit: contain;
        /* Asegura que la imagen se escale correctamente */
    }

    .checkbox-container {
    margin: 10px;
    color: #ffffff;
    background-color: #333;
    display: flex;
    align-items: center;
    justify-content: space-between;
    }

    .vlan-dropdown-container {
    display: flex;
    align-items: center;
    justify-content: center;
    flex-grow: 1;
    }

    .vlan-dropdown-container label {
    margin-right: 10px;
    white-space: nowrap;
    }

    #vlan-select {
    padding: 5px;
    border-radius: 4px;
    background-color: #ffffff;
    color: #333;
    }

    .left-controls {
    display: flex;
    align-items: center;
    justify-content: flex-end;
    }

    .right-controls {
    display: flex;
    align-items: center;
    justify-content: flex-end;
    }

    .elapsed-time {
    margin-left: 15px;
    white-space: nowrap;
    }
</style>
