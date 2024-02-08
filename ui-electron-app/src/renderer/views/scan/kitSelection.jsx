import React, { useState, useCallback, useEffect } from 'react';
import {
  createStyles,
  Text,
  Group,
  Button,
  ScrollArea,
  Card,
  Checkbox,
  Alert,
  SimpleGrid,
  UnstyledButton,
  Popover,
  Modal
} from '@mantine/core';
import {
  ArrowLeft, ArrowRight, InfoCircle
} from 'tabler-icons-react';
import { Link, useNavigate } from 'react-router-dom';
import { useDispatch, useSelector } from 'react-redux';
import { setProduct as setScanProduct } from '../../features/scan/scanSlice.js';
import { productSelector, setProduct } from '../../features/product/productSlice.js';
import { AppShellHeader } from '../../components/AppShellHeader.jsx';
import { SubHeading } from '../../components/SubHeading.jsx';
import { IllustrationKit } from '../../assets/IllKit.js';
import { textClamp } from '../../../lib/util/textClamp.js';
import { IllustrationPlateLoad } from '../../assets/IllPlateLoad.js';
import { getProducts } from '../../actions/productActions.js';
import { Flow } from './../../enums/Flow.js';
import { ProductPopover } from '../../components/ProductPopover.jsx';
import { useAppStyles } from '../../styles/appStyles.js';

const useStyles = createStyles(useAppStyles);

const KitSelection = ({ ...props }) => {
  const products = useSelector(productSelector)?.products;
  const [selectedProduct, setSelectedProduct] = useState({ productId: '', productName: '' });
  const [showPopover, setShowPopover] = useState({ productId: '', show: false });
  const [modalOpen, setModalOpen] = useState(false);
  const dispatch = useDispatch();
  const { classes, cx } = useStyles();
  const flowType = useSelector((state) => (state.flow.type));
  const analysis = useSelector((state) => (state.analysis)); //TODO: where is this initially set?
  const navigate = useNavigate();

  useEffect(() => {
    dispatch(getProducts({ excludeCalibrationPlates: true }));
  }, []);

  const handleSelectProduct = (product) => {
    // https://auragentbioscience.slack.com/archives/D03FEDPMN31/p1661182830585999
    // the ID should be the product's _id
    setSelectedProduct({ productId: `${product?._id}`, productName: product?.productName });
    dispatch(setProduct({
      ...product,
      productId: `${product?._id}`
    }));
  };

  useEffect(() => {

    if (flowType === Flow.MANAGE_ANALYSIS_TEMPLATES) {
      const product = products?.find((p) => p.id === analysis?.template?.productId);
      handleSelectProduct(product);
    }

    // TODO: preselect product if only one product exists?

  }, [products, analysis]);

  return (
    <>
      <AppShellHeader className={classes.mainHeader} screenTitle={props.screenTitle}>
        {/* Group at position start in AppShellHeader component with title prop */}
        <Group position="end">
          <Button className={classes.secondaryNavigationButton} variant="default" leftIcon={<ArrowLeft size={18} />} onClick={() => navigate('/', { replace: true })}>
            Back
          </Button>

          <Button
            type="button"
            className={classes.navigationButton}
            rightIcon={<ArrowRight size={18} />}
            onClick={() => (
              flowType === 'MANAGE_ANALYSIS_TEMPLATES'
                ? navigate('/manage-templates/analysis-temps-three', { replace: true })
                : setModalOpen(true)
            )}
            disabled={selectedProduct.productId === ''}
          >
            Continue
          </Button>
        </Group>
      </AppShellHeader>

      <div className={classes.appBackground}>
        <ScrollArea sx={{ height: 'calc(100vh - 113px)', padding: '30px 40px' }}>

          <Text size="sm" className={classes.title}>Available Products/Kits</Text>
          <Text className={classes.text}>Select a product/kit from the available options to continue.</Text>

          <SimpleGrid cols={3} mt={35} spacing={28} sx={{ maxWidth: 815 }}>
            {products?.map((product) => (
              <Card
                // withBorder
                className={classes.card}
                sx={(t) => ({
                  maxWidth: '250px',
                  // border: `solid 2px ${selectedProduct.productId === product._id ? t.colors.blue[6] : t.colors.gray[2]}`
                })}
                key={product?._id || product?.id} // legacy support for id
              >
                <Card.Section style={{ padding: 24, textAlign: 'center' }}>
                  <IllustrationKit />
                </Card.Section>

                <Card.Section style={{ padding: 24, textAlign: 'center', maxHeight: '80px' }}>
                  <div style={{ minHeight: 38, marginBottom: 5 }}>
                    <SubHeading fontSize={12} centered>{product?.productName}</SubHeading>
                  </div>

                  <Text
                    className={classes.text}
                    sx={{ minHeight: 41, fontSize: 12 }}
                  >
                    {textClamp(`${Object.values(product?.productDescription).reduce((acc, curr) => acc + curr, '') || 'no description'}`, 60)}
                    {' '}
                    <ProductPopover setShowPopover={setShowPopover} showPopover={showPopover} product={product} styleClasses={classes} />
                  </Text>
                </Card.Section>

                <Card.Section>
                  {/* eslint-disable-next-line jsx-a11y/label-has-associated-control */}
                  <label
                    htmlFor={product.productName}
                    style={{
                      display: 'grid',
                      gridTemplateColumns: '1fr 1fr 1fr',
                      gridTemplateRows: '1fr',
                      gap: '0 0',
                      gridTemplateAreas: '"left middle right"',
                      marginTop: '16px',
                      padding: '16px 16px',
                      borderTop: 'solid 1px #e2e2e2'
                    }}
                  >
                    <Text sx={{ gridArea: 'middle', justifySelf: 'center' }}>Select</Text>
                    <Checkbox
                      name={product.productName}
                      id={product.productName}
                      aria-label="Select"
                      checked={selectedProduct.productId === `${product._id}`}
                      radius="xl"
                      color="green"
                      onChange={() => handleSelectProduct(product)}
                      sx={{ gridArea: 'right', justifySelf: 'flex-end' }}
                    />
                  </label>
                </Card.Section>
              </Card>
            ))}
          </SimpleGrid>
        </ScrollArea>
      </div>


      <Modal
        opened={modalOpen}
        onClose={() => setModalOpen(false)}
        closeOnClickOutside={false}
        closeOnEscape={false}
        size={375}
        centered
        styles={{
          header: { marginBottom: 0 },
          body: { textAlign: 'center' }
        }}
      >
        <Text size="lg" weight={600} mb={28}>Load plate into Reader</Text>

        <IllustrationPlateLoad />

        <Text size="sm" color="dimmed" mb={15} mt={28}>
          Before being able to move to the next screen,
          <br />
          please confirm that the Plate is loaded correctly
          <br />
          into the Empower Reader.
        </Text>

        <Button
          type="button"
          color="green"
          size="md"
          onClick={() => {
            dispatch(setScanProduct({ product: { productId: selectedProduct.productId, productName: selectedProduct?.productName } }));
            navigate('/scan/scan-two', { replace: true });
          }}
          mt={30}
          mb={20}
        >
          Confirm
        </Button>
      </Modal>
    </>
  );
}

export default KitSelection;