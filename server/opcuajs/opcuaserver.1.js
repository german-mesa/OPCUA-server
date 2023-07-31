/*global require, setInterval, console */

// Import the required module
const opcua = require("node-opcua");

// Define the security policies for the server
const securityPolicies = [
    opcua.SecurityPolicy.Basic128Rsa15,
    opcua.SecurityPolicy.Basic256,
];


// Let's create an instance of OPCUAServer with security configurations
const server = new opcua.OPCUAServer({
    port: 4334,                             // The port of the listening socket of the server
    resourcePath: "/UA/BatteryCellServer",   // This path will be added to the endpoint resource name
    buildInfo: {
        productName: "BatteryCellServer",   // Name of the product associated with the server
        buildNumber: "7658",                // Build number of the server
        buildDate: new Date(2023, 7, 21)    // Build date of the server (July 21, 2023)
    }
});

// Function to be called after server initialization
function post_initialize() {
    console.log("initialized");

    server.serverInfo.applicationName.text = 'Battery Cell Manufacturing Server';

    server.securityPolicies = [
      opcua.SecurityPolicy.None,
      opcua.SecurityPolicy.Basic256Sha256,
      opcua.SecurityPolicy.Basic256Sha256,
    ];

    server.start(function() {
        console.log("Server is now listening ... ( press CTRL+C to stop)");
        console.log(server.endpoints[0].port, " is the port");
        const endpointUrl = server.endpoints[0].endpointDescriptions()[0].endpointUrl;
        console.log(endpointUrl, " is the primary server endpoint url");
    });
}


// Initialize the server and call post_initialize() when done
server.initialize(post_initialize);

