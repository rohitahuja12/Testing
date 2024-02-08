import React from "react";
import { rest, setupWorker } from "msw";
import { screen, cleanup } from "@testing-library/react";
import BBViewAnalysisTemplates from "../components/brightestBio/pages/BBViewAnalysisTemplates";
import { renderWithProviders } from "../testUtils/test-utils.jsx";
import { server } from "../mocks/server";

beforeAll(() => server.listen());
afterEach(() => {
  server.resetHandlers();
  cleanup();
});
afterAll(() => server.close());

const mockedUsedNavigate = jest.fn();
jest.mock("react-router-dom", () => ({
  ...jest.requireActual("react-router-dom"),
  useNavigate: () => mockedUsedNavigate,
}));

test("analysis templates table renders", async () => {
  renderWithProviders(<BBViewAnalysisTemplates />);

  const templatesTextFound = await screen.findAllByText(/Standards2/i);
  expect(templatesTextFound.length).toBeGreaterThan(0);
})