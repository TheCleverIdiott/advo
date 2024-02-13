const Docs = require("../models/docs.model");

const getDocs = async (req, res) => {
    try {
        const docs = await Docs.find();
        res.status(200).json(docs);
    } catch (error) {
        res.status(404).json({ message: error.message });
    }
    }

const getDoc = async (req, res) => {
    try{
        const doc = await Docs.findById(req.params.id);
        res.status(200).json(doc);
    } catch (error) {
        res.status(404).json({ message: error.message });

    }
}

const postDoc = async (req, res) => {
    const doc = req.body;
    const newDoc = new Docs(doc);
    try {
        await newDoc.save();
        res.status(201).json(newDoc);
    } catch (error) {
        res.status(409).json({ message: error.message });
    }
}

const deleteDoc = async (req, res) => {
    try {
        await Docs.findByIdAndRemove(req.params.id);
        res.status(200).json({ message: "Deleted successfully" });
    } catch (error) {
        res.status(404).json({ message: error.message });
    }
}

const updateDoc = async (req, res) => {
    try{
        await Docs.findByIdAndUpdate(req.params.id, req.body);
        res.status(200).json({ message: "Updated successfully" });
    } catch (error) {
        res.status(404).json({ message: error.message });

    }
}

module.exports = {
    getDocs,
    getDoc,
    postDoc,
    deleteDoc,
    updateDoc
}

