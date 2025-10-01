import React from 'react';
import {
  Box,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Button,
  Card,
  CardContent,
  Typography,
  useTheme,
  Chip,
  styled,
} from '@mui/material';
import { CheckCircle } from '@mui/icons-material';
import type { AIApplication } from '../types';

const GlowingButton = styled(Button)(({ theme }) => ({
  transition: 'all 0.3s ease',
  ...(theme.palette.mode === 'dark' && {
    '&:hover': {
      boxShadow: '0 0 15px rgba(255, 165, 0, 0.3)',
    },
  }),
}));

interface ApplicationDropdownSelectorProps {
  applications: AIApplication[];
  selectedApp: string | null;
  onSelectionChange: (selectedApp: string) => void;
  onSubmit: () => void;
}

const ApplicationDropdownSelector: React.FC<ApplicationDropdownSelectorProps> = ({
  applications,
  selectedApp,
  onSelectionChange,
  onSubmit,
}) => {
  const theme = useTheme();
  const isDarkMode = theme.palette.mode === 'dark';

  const handleApplicationChange = (event: any) => {
    onSelectionChange(event.target.value);
  };

  const handleSubmit = () => {
    if (selectedApp) {
      onSubmit();
    }
  };

  const getSelectedApplication = () => {
    return applications.find(app => app.id === selectedApp);
  };

  const selectedApplication = getSelectedApplication();

  return (
    <Card sx={{ mb: 3 }}>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          Select AI Application
        </Typography>
        
        <Box sx={{ display: 'flex', flexDirection: { xs: 'column', sm: 'row' }, gap: 2, alignItems: { xs: 'stretch', sm: 'flex-end' } }}>
          {/* Application Dropdown */}
          <FormControl fullWidth size="small" sx={{ '& .MuiFormLabel-root': { fontSize: '0.875rem' } }}>
            <InputLabel id="application-select-label">Choose Application</InputLabel>
            <Select
              labelId="application-select-label"
              id="application-select"
              value={selectedApp || ''}
              label="Choose Application"
              onChange={handleApplicationChange}
              sx={{
                fontSize: '0.875rem', // Consistent font size with button
                '& .MuiSelect-select': {
                  py: '8px', // Consistent padding with button
                },
                ...(isDarkMode && {
                  '&:hover .MuiOutlinedInput-notchedOutline': {
                    borderColor: 'rgba(255, 165, 0, 0.5)',
                    boxShadow: '0 0 8px rgba(255, 165, 0, 0.2)',
                  },
                  '&.Mui-focused .MuiOutlinedInput-notchedOutline': {
                    borderColor: theme.palette.primary.main,
                    boxShadow: '0 0 12px rgba(255, 165, 0, 0.3)',
                  },
                }),
              }}
            >
              <MenuItem value="">
                <em>Select an application...</em>
              </MenuItem>
              {applications.map((app) => (
                <MenuItem key={app.id} value={app.id}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    {typeof app.icon === 'string' ? (
                      <span style={{ fontSize: '16px' }}>{app.icon}</span>
                    ) : (
                      (() => {
                        const IconComponent = app.icon;
                        return <IconComponent width={16} height={16} style={{ color: app.color }} />;
                      })()
                    )}
                    <span>{app.displayName}</span>
                  </Box>
                </MenuItem>
              ))}
            </Select>
          </FormControl>

          {/* Submit Button */}
          <GlowingButton
            variant="contained"
            onClick={handleSubmit}
            disabled={!selectedApp}
            sx={{ 
              minWidth: '120px',
              height: '40px', // Match Material-UI small size height
              px: 2, // Consistent padding with dropdown
              borderRadius: 1, // Match dropdown border radius
              fontSize: '0.875rem', // Match dropdown text size
            }}
          >
            <CheckCircle sx={{ mr: 1, fontSize: 16 }} />
            Load Metrics
          </GlowingButton>
        </Box>

        {/* Selected Application Display */}
        {selectedApplication && (
          <Box sx={{ mt: 3, pt: 2, borderTop: 1, borderColor: 'divider' }}>
            <Typography variant="body2" color="text.secondary" gutterBottom>
              Selected Application:
            </Typography>
            <Chip
              icon={
                typeof selectedApplication.icon === 'string' ? (
                  <span style={{ fontSize: '14px' }}>{selectedApplication.icon}</span>
                ) : (
                  (() => {
                    const IconComponent = selectedApplication.icon;
                    return <IconComponent width={16} height={16} style={{ color: 'white' }} />;
                  })()
                )
              }
              label={selectedApplication.displayName}
              sx={{
                bgcolor: selectedApplication.color,
                color: 'white',
                fontWeight: 'medium',
              }}
            />
          </Box>
        )}
      </CardContent>
    </Card>
  );
};

export default ApplicationDropdownSelector;