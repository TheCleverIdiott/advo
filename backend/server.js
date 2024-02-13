const { urlencoded } = require("express");
const express = require("express");
const path = require("path");
const cookieParse = require("cookie-parser");
const bodyParser = require('body-parser')
const session = require('express-session')
const mongodbStore = require('connect-mongodb-session')(session)
const cors = require('cors')
const multer = require('multer')

require("dotenv").config();
require("./db/conn");

const views_path = path.join(__dirname, "/views");
const static_path = path.join(__dirname, "/static");
const Auth = require('./routes/auth.route')

const app = express();
const port = process.env.PORT || 80;

const store = new mongodbStore({
    uri: process.env.MONGO_URI,
    collection: 'sessions'
})

app.use(cors({
    origin: '*',
    credentials: true
}))

app.use(session({ secret: process.env.SECRET_KEY, resave: false, saveUninitialized: false, store: store, cookie: {maxAge: 12 * 60 * 60 * 1000}}))

app.use("/static", express.static(static_path));
app.use(express.json());
app.use(urlencoded({ extended: true }));
app.use(cookieParse());
app.use(bodyParser.urlencoded({ extended: true }))
app.use(bodyParser.json())


app.set("view engine", "ejs");
app.set("views", views_path);

app.use(Auth)

app.listen(port, () => {
    console.log(`The application started successfully on port ${port}`);
});

app.get('/', (req, res) => {
    res.send({"server_status": "ok"})
})