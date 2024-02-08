import { screen } from "@testing-library/react";
import Dashboard from "./../views/dashboard.jsx";
import React from "react";
import { renderWithProviders } from "../testUtils/test-utils.jsx";

const mockedUsedNavigate = jest.fn();
jest.mock("react-router-dom", () => ({
  ...jest.requireActual("react-router-dom"),
  useNavigate: () => mockedUsedNavigate,
}));

/**
 * No settings exist in the mantine view,
 * so we can use this to test if we are in the mantine view
 * or the mui view.
 */
test("dashboard renders with mui by default", async () => {
  renderWithProviders(<Dashboard />);
  const settingsTextFoundArr = await screen.findAllByText(/Settings/i);
  expect(settingsTextFoundArr.length).toBeGreaterThan(0);
});
