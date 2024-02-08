import React from 'react';
import { Text } from '@mantine/core';

export function SubHeading({ children, ...props }) {
  const { centered, fontSize } = props;

  return (
    <Text
      sx={(theme) => ({
        marginBottom: 15,
        textAlign: centered ? 'center' : 'left',
        fontWeight: 700,
        fontSize: fontSize || theme.fontSizes.sm
      })}
    >
      {children}
    </Text>
  );
}
