const mongoose = require('mongoose');


const url = String(process.env.MONGO_URI); 
mongoose.connect(url, {
    useNewUrlParser: true,
    useUnifiedTopology: true
});


let db = mongoose.connection;
db.on("error", console.error.bind(console, "connection error: "));
db.once("open", function () {
    console.log("We are connected");
});
