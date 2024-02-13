const mongoose = require('mongoose')

const docSchema = new mongoose.Schema({
    licenseID: {
        type: String,
        required: true,
        unique: true
    },
    documents: [
        {
            url:{
                type: String,
                required: true
            },
            fileType: {
                type: String,
                required: true
            }
        }
    ],
    cleanText:{
        type: String,
    },
    keywords: [
        {
            type: String
        }
    ],
    summary: {
        type: String
    }     
})

const Docs = mongoose.model('Doc', docSchema)

module.exports = Docs