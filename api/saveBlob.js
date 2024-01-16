// saveBlob.js
import { put } from "@vercel/blob";

module.exports = async (req, res) => {
  try {
    // Extract JSON data from the request body
    const { json_data } = req.body;

    // Save the JSON data to the Blob store
    const { url } = await put('articles/blob.txt', json_data, { access: 'public' });

    // Respond with the URL where the data is stored
    res.status(200).json({ url });
  } catch (error) {
    // Handle errors
    res.status(500).send('Error storing data in Blob store.');
  }
};