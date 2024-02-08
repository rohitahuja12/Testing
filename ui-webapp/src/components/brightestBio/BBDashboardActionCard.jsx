import React, { useState, useCallback, useEffect, useMemo } from 'react';
import {
  Button,
  Card,
  CardContent,
  CardMedia,
  CardActions,
  CardActionArea,
  Typography,
} from '@mui/material';
import { grey } from '@mui/material/colors';
import { blueGrey } from '@mui/material/colors';
import { useTheme } from '@mui/material/styles';

/**
 * 
 * @param {{ 
 * title: string, 
 * description: string, 
 * image: any,
 * imageAlt: string,
 * actionButtons: Array<{name: string, action: function}> 
 * defaultAction: function
 * compact: boolean
 * }} props 
 */
const BBDashboardActionCard = ({
  title,
  description,
  image,
  actionButtons,
  imageAlt,
  defaultAction = () => {},
  compact = false,
}) => {
  const theme = useTheme();
  const cardSxOptions = useMemo(() => compact ? { minHeight: '50%' } : { minHeight: '100%' }, [compact]);
  const cardContentSxOptions = useMemo(() => compact ? { minHeight: '6em' } : { minHeight: '5em' }, [compact]);

  return (
    <Card sx={{ ...cardSxOptions, border: theme.palette.mode === 'dark' ? 1 : 0, borderColor: grey[900] }}>
      <CardActionArea onClick={defaultAction}>
        {image
          && <CardMedia
            component="img"
            height="140"
            image={image || ""}
            alt={imageAlt || "sample image"}
            sx={{ padding: "2em 1em 1em 0em", objectFit: "contain" }}
          />}

        <CardContent sx={cardContentSxOptions}>
          <Typography gutterBottom variant="h5" component="div">
            {title || ""}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            {description || ""}
          </Typography>
        </CardContent>
      </CardActionArea>
      <CardActions>
        {actionButtons?.map((button) => {
          return (
            <Button
              size="small"
              color="secondary"
              onClick={button.action}
              key={button.name}
            >
              {button.name}
            </Button>
          );
        })}
      </CardActions>
    </Card>
  )
}

export default BBDashboardActionCard;