import weaviate from "weaviate-ts-client";
import { readdirSync, readFileSync, writeFileSync } from "fs";
import path from "path";

(async () => {
  const client = weaviate.client({
    scheme: "http",
    host: "localhost:8080",
  });

  try {
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
    //storing images in the database

    const folderPath = "./static/uploads";
    const files = readdirSync(folderPath);

    for (const file of files) {
      const filePath = path.join(folderPath, file);
      const img = readFileSync(filePath);
      const b64 = Buffer.from(img).toString("base64");

      await client.data
        .creator()
        .withClassName("Meme")
        .withProperties({
          image: b64,
          text: path.parse(file).name, // Use the file name without extension as the text
        })
        .do();

      console.log(`Data for ${file} added to 'Meme' class.`);
    }
    //querying the database
    const test = Buffer.from(readFileSync("./test3_img.jpeg")).toString(
      "base64"
    );
    const resImage = await client.graphql
      .get()
      .withClassName("Meme")
      .withFields(["image"])
      .withNearImage({ image: test })
      .withLimit(1)
      .do();

    // Write result to filesystem
    const result = resImage.data.Get.Meme[0].image;
    writeFileSync("./result.jpg", result, "base64");

    console.log("Image processing and retrieval completed successfully.");
  } catch (error) {
    console.error("An error occurred:", error);
  }
})();
