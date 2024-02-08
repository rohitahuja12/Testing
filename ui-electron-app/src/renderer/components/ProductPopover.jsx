import React from 'react';
import {
    Text,
    UnstyledButton,
    Popover,
    createStyles,
} from '@mantine/core';
import { InfoCircle } from 'tabler-icons-react';
import { useAppStyles } from '../styles/appStyles';

const useStyles = createStyles(useAppStyles);

export const ProductPopover = ({
    setShowPopover,
    showPopover,
    product
}) => {

    const { classes, cx } = useStyles();

    return (<Popover
        opened={showPopover.productId === `${product._id}` && showPopover.show}
        position="bottom"
        onClose={() => setShowPopover({ productId: '', show: false })}
        withCloseButton
        title={product.name}
        width={300}
        target={(
            <UnstyledButton
                className={classes.popoverLink}
                onClick={() => setShowPopover({ productId: `${product._id}`, show: true })}
                sx={(t) => ({ fontSize: 12})}
            >
                Details
                <InfoCircle size={10}/>
            </UnstyledButton>
        )}
    >
        <Text color="blue" className={classes.title} mb={15}>Product Details</Text>

        <Text size="sm" className={classes.title}>Format:</Text>
        {/* TODO: use actual keys and make this pretty */}
        <Text size="sm" className={classes.text}>{typeof product.productDescription === 'string'
            ? product.productDescription
            : Object.values(product.productDescription).join(',')}</Text>

        <Text size="sm" className={classes.title} mt={15}>Analytes Detected:</Text>

        {<Text size="sm" className={classes.text}>{product?.recommendedInitialConcentrations ? Object.keys(product?.recommendedInitialConcentrations).join(', ') : 'no recommended initial concentrations found'}</Text>}
    </Popover>)
}