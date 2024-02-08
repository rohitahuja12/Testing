import products from './../../utils/mock-data/products.json';
import { getUniqueProducts } from '../../actions/productActions'

test('Kit Selection -> unique products are retrieved', async () => {
    expect(getUniqueProducts(products).length).toBeGreaterThan(0);
    expect(getUniqueProducts(products).length).toEqual(2);
})