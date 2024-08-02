// Import required modules
const { urlencoded } = require("express");
const express = require("express");
const path = require("path");
const cookieParse = require("cookie-parser");
const bodyParser = require('body-parser');
const session = require('express-session');
const mongodbStore = require('connect-mongodb-session')(session);
const cors = require('cors');
const multer = require('multer');

// Load environment variables from .env file
require("dotenv").config();

// Connect to the database
require("./db/conn");

// Define paths for views and static files
const views_path = path.join(__dirname, "/views");
const static_path = path.join(__dirname, "/static");

// Import routes
const Auth = require('./routes/auth.route');

// Initialize Express app
const app = express();
const port = process.env.PORT || 80; // Set the port from environment variable or default to 80

// Configure session store to use MongoDB
const store = new mongodbStore({
    uri: process.env.MONGO_URI,
    collection: 'sessions'
});

// Enable CORS for all origins
app.use(cors({
    origin: '*',
    credentials: true
}));

// Configure session management with MongoDB store
app.use(session({
    secret: process.env.SECRET_KEY, 
    resave: false, 
    saveUninitialized: false, 
    store: store, 
    cookie: { maxAge: 12 * 60 * 60 * 1000 } // 12 hours
}));

// Serve static files from the /static directory
app.use("/static", express.static(static_path));

// Middleware to parse JSON and urlencoded data
app.use(express.json());
app.use(urlencoded({ extended: true }));
app.use(cookieParse());
app.use(bodyParser.urlencoded({ extended: true }));
app.use(bodyParser.json());

// Set view engine to EJS and define views directory
app.set("view engine", "ejs");
app.set("views", views_path);

// Use authentication routes
app.use(Auth);

// Start the server and listen on the defined port
app.listen(port, () => {
    console.log(`The application started successfully on port ${port}`);
});

// Define a route for the root URL
app.get('/', (req, res) => {
    res.send({"server_status": "ok"});
});
