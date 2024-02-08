import { rest } from "msw";
import { analysisTemplates } from "./analysisTemplates.data";

const handlers = [
  rest.get("http://localhost:5000/analysisTemplates", (req, res, ctx) => {
    return res(ctx.json(analysisTemplates), ctx.delay(150));
  }),
];

export default handlers;