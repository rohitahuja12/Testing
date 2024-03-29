import React from 'react'
import { render } from '@testing-library/react'
import { configureStore } from '@reduxjs/toolkit'
import { Provider } from 'react-redux'
// As a basic setup, import your same slice reducers
import { setupMockStore } from '../store'
import { Flow } from './../enums/Flow.js';
import * as products from './mock-data/products.json';

export function renderWithProviders(
  ui,
  {
    //state.flow.type = 'scan',
    //useSelector(productSelector)?.products
    //state.analysis
    preloadedState = {
      flow: {
        type: Flow.SCAN
      },
      product: {
        products: []
      }
    },
    // Automatically create a store instance if no store was passed in
    store = setupMockStore(preloadedState),
    ...renderOptions
  } = {}
) {
  function Wrapper({ children }) {
    return <Provider store={store}>{children}</Provider>
  }

  // Return an object with the store and all of RTL's query functions
  return { store, ...render(ui, { wrapper: Wrapper, ...renderOptions }) }
}