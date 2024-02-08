import { useState, useCallback, useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { getProducts } from '../../../actions/productActions';
import { productSelector } from '../../../features/product/productSlice.js';
import { plateSelector } from '../../../features/plates/plateSlice';
import { getPlates } from '../../../actions/plates';

export const useProducts = () => {
  const dispatch = useDispatch();
  const products = useSelector(productSelector)?.products;
  const plates = useSelector(plateSelector);
  const [selectedProduct, setSelectedProduct] = useState(null);
  const [selectedPlate, setSelectedPlate] = useState(null);


  useEffect(() => {
    dispatch(getProducts({ excludeCalibrationPlates: true }));
    dispatch(getPlates());
  }, [dispatch]);

  /**
   * @param {string} productId
   */
  const getProductById = useCallback(
    (productId) => {
      return products.find((product) => product._id === productId);
    },
    [products]
  );

  /**
   * @param {string} barcode
   * @returns {object} product
   * @throws {Error} if plate not found
   * @throws {Error} if product not found
   * @description (phx-225) Returns the product that has the given plate barcode.
   */
  const selectProductByBarcode = useCallback(
    (barcode) => {
      const plate = plates.find((plate) => plate.barcode === barcode);
      setSelectedPlate(null);
      if (!plate) {
        setSelectedProduct(null);
        throw new Error('Plate not found');
      }
      const product = getProductById(plate.productId);
      setSelectedProduct(product);
      if (!product) throw new Error('Product not found');

      return product;
    },
    [plates, products, getProductById, setSelectedProduct]
  );

  /**
   * @param {string} productId
   * @returns {string} barcode
   * @throws {Error} if plate not found
   * @description (phx-229) Returns the barcode of the plate that has the given productId. 
   */
  const getPlateBarcodeByProductId = useCallback(
    (productId) => {
      const plate = plates.find((plate) => plate.productId === productId);
      if (!plate) return new Error('Plate not found');
      return plate.barcode;
    },
    [plates]
  );

  return {
    products,
    selectedProduct,
    setSelectedProduct,
    getProductById,
    plates,
    selectProductByBarcode,
    getPlateBarcodeByProductId,
    selectedPlate
  };
}
