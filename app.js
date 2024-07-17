import express from "express";
import weaviate from "weaviate-ts-client";
import { readdirSync, readFileSync, writeFileSync } from "fs";
import path from "path";
import multer from "multer";
import { clear } from "console";

const __dirname = path.dirname(new URL(import.meta.url).pathname);

const app = express();
const port = 3000;

const upload = multer({ dest: path.join(__dirname, "public/uploads/") });

const client = weaviate.client({
  scheme: "http",
  host: "localhost:8080",
});

app.set("view engine", "ejs");
app.use(express.static(path.join(__dirname, "public")));

const initializeWeaviate = async () => {
  const schemaRes = await client.schema.getter().do();
  console.log(schemaRes);

  const classExists = schemaRes.classes.some((cls) => cls.class === "Meme");

  if (!classExists) {
    const schemaConfig = {
      class: "Meme",
      vectorizer: "img2vec-neural",
      vectorIndexType: "hnsw",
      moduleConfig: {
        "img2vec-neural": {
          imageFields: ["image"],
        },
      },
      properties: [
        {
          name: "image",
          dataType: ["blob"],
        },
        {
          name: "text",
          dataType: ["string"],
        },
      ],
    };

    await client.schema.classCreator().withClass(schemaConfig).do();
    console.log("Class 'Meme' created successfully.");
  } else {
    console.log("Class 'Meme' already exists.");
  }

  const clearDatabase = async () => {
    // Fetch all objects in the "Meme" class
    const res = await client.graphql
      .get()
      .withClassName("Meme")
      .withFields(["_additional { id }"])
      .withLimit(1000) // Adjust the limit if you have more than 1000 objects
      .do();

    const ids = res.data.Get.Meme.map((obj) => obj._additional.id);
    console.log(ids);
    // Delete each object by id
    for (const id of ids) {
      await client.data.deleter().withClassName("Meme").withId(id).do();
      console.log(`Deleted object with id: ${id}`);
    }
  };

  // Store images in the database
  const folderPath = path.join(__dirname, "public/uploads");
  const files = readdirSync(folderPath);

  // Retrieve all existing images from the database
  const existingImagesRes = await client.graphql
    .get()
    .withClassName("Meme")
    .withFields(["image"])
    .withLimit(1000) // Adjust the limit based on your requirements
    .do();
  const existingImages = existingImagesRes.data.Get.Meme.map(
    (meme) => meme.image
  );

  for (const file of files) {
    const filePath = path.join(folderPath, file);
    const img = readFileSync(filePath);
    const b64 = Buffer.from(img).toString("base64");

    // Check if the image already exists in the database
    if (!existingImages.includes(b64)) {
      await client.data
        .creator()
        .withClassName("Meme")
        .withProperties({
          image: b64,
          text: path.parse(file).name, // Use the file name without extension as the text
        })
        .do();

      console.log(`Data for ${file} added to 'Meme' class.`);
    } else {
      console.log(`Data for ${file} already exists in 'Meme' class.`);
    }
  }
};

app.get("/", (req, res) => {
  res.render("index");
});

app.post("/upload", upload.single("image"), async (req, res) => {
  const file = req.file;
  const filePath = path.join(__dirname, "public/uploads", file.filename);

  const test = Buffer.from(readFileSync(filePath)).toString("base64");

  const resImage = await client.graphql
    .get()
    .withClassName("Meme")
    .withFields(["image"])
    .withNearImage({ image: test })
    .withLimit(6)
    .do();

  const queryImage = test;
  const resultImages = resImage.data.Get.Meme.map((meme) => meme.image);

  // Filter out the query image from the result images
  const uniqueResultImages = resultImages.filter(
    (image) => image !== queryImage
  );

  // Save the result images to the filesystem
  uniqueResultImages.forEach((image, index) => {
    const resultFilePath = path.join(
      __dirname,
      "public",
      `result${index + 1}.jpg`
    );
    writeFileSync(resultFilePath, image, "base64");
  });

  res.render("result", {
    queryImage: file.filename,
    resultImages: uniqueResultImages.map(
      (_, index) => `result${index + 1}.jpg`
    ),
  });
});

app.listen(port, async () => {
  await initializeWeaviate();
  console.log(`Server is running on http://localhost:${port}`);
});
