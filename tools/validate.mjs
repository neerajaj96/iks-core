import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const root = join(dirname(fileURLToPath(import.meta.url)), "..");
const schema = JSON.parse(readFileSync(join(root, "schema", "iks-schema.json"), "utf-8"));
if (!schema.definitions || !JSON.stringify(schema).includes("Text")) {
  console.error("schema INVALID");
  process.exit(1);
}
console.log("schema OK");
for (const name of ["texts.json", "sutras.json", "terms.json", "inferences.json",
                    "cognitions.json", "vada_nodes.json", "vada_edges.json"]) {
  const d = JSON.parse(readFileSync(join(root, "data", name), "utf-8"));
  console.log(name, "records:", d.length);
}
