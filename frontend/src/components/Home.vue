<template>
    <main>
      <h3 class="centered-heading">{{ message }}</h3>
      <p class="centered-time">{{ time }}</p>
    </main>
  </template>
  
  <script>
  import axios from 'axios';
  
  export default {
    name: "Home",
    data() {
      return {
        message: 'Loading...', // Initial message before the API call response
        time: '' // Initial time before the API call response
      };
    },
    mounted() {
      this.fetchData();
    },
    methods: {
      async fetchData() {
        
        const protocol = import.meta.env.VITE_API_PROTOCOL;
        const host = import.meta.env.VITE_API_HOST;
        const port = import.meta.env.VITE_API_PORT;
        const endpoint = import.meta.env.VITE_API_ENDPOINT_ROOT;
        const url = `${protocol}://${host}:${port}${endpoint}`;
  
        try {
          const response = await axios.get(url);
          this.message = response.data.message; // Update the message with the API response
          this.time = response.data.time; // Update the time with the API response
        } catch (error) {
          console.error('There was a problem with the axios request:', error);
          this.message = 'Failed to load message';
          this.time = 'Failed to load time';
        }
      }
    }
  };
  </script>
  
  <style>
  body {
    background-color: #333;
  }
  
  .centered-heading {
    text-align: center;
    color: white; /* This ensures the text is visible against the black background */
  }
  
  .centered-time {
    text-align: center;
    color: #ccc; /* Lighter color for the time to distinguish it from the message */
  }
  </style>
  