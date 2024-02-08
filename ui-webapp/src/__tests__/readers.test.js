import React from "react";
import { rest, setupWorker } from "msw";
import { setupServer } from "msw/node";
import { screen, cleanup } from "@testing-library/react";
import BBViewReaders from "../components/brightestBio/pages/BBViewReaders.jsx";
import { renderWithProviders } from "../testUtils/test-utils.jsx";
import { waitFor } from "@testing-library/react";

const readers = [
  {
    _id: "1",
    serialNumber: "089d0uf",
    status: {
      door: "open",
      laser: "on",
    },
  },
];
export const handlers = [
  rest.get("http://localhost:5000/readers", (req, res, ctx) => {
    return res(ctx.status(200), ctx.json(readers));
    // return res(ctx.json(readers), ctx.delay(150));
  }),
];

const server = setupServer(...handlers);

// Enable API mocking before tests.
beforeAll(() => server.listen());

// Reset any runtime request handlers we may add during the tests.
afterEach(() => {
  server.resetHandlers();
  cleanup();
});

// Disable API mocking after the tests are done.
afterAll(() => server.close());

const mockedUsedNavigate = jest.fn();
jest.mock("react-router-dom", () => ({
  ...jest.requireActual("react-router-dom"),
  useNavigate: () => mockedUsedNavigate,
}));

test("readers table renders", async () => {
  renderWithProviders(<BBViewReaders />, {
    reader: {
      serialNumber: "3",
      readers,
    },
  });
  const readersTextFoundArr = await screen.findAllByText(/089d0uf/i);
  expect(readersTextFoundArr.length).toBeGreaterThan(0);
  const colSerialNumber = await screen.findByText("Serial Number");
  expect(colSerialNumber).toBeInTheDocument();
  const colDoor = await screen.findByText("Door");
  expect(colDoor).toBeInTheDocument();
  const colLaser = await screen.findByText("Laser");
  expect(colLaser).toBeInTheDocument();
});