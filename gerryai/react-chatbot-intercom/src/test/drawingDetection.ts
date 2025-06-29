// Test drawing detection regex
const testMessages = [
  "draw a cat",
  "create an image of a sunset",
  "generate a picture of mountains",
  "make a drawing of a car",
  "paint a landscape",
  "sketch a house",
  "illustrate a dog",
  "hello how are you",
  "what is the weather",
  "Draw me a beautiful flower",
  "Can you create an artwork of the ocean?",
  "Please generate an illustration of a robot"
];

const isDrawingRequest = (text: string) => {
  return /\b(draw|create|generate|make|paint|sketch|illustrate).*\b(image|picture|artwork|drawing|illustration|painting)/i.test(text) ||
         /^(draw|create|generate|make|paint|sketch|illustrate)\s+/i.test(text.trim());
};

console.log("Drawing detection test results:");
testMessages.forEach(msg => {
  console.log(`"${msg}" -> ${isDrawingRequest(msg) ? "DRAW" : "CHAT"}`);
});

export {};
