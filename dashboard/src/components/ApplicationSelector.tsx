import React from 'react';
import {
  Box,
  Chip,
  FormControlLabel,
  Checkbox,
  Card,
  CardContent,
  Typography,
  Button,
  useTheme,
  styled,
} from '@mui/material';
import type { AIApplication } from '../types';

const GlowingCard = styled(Card)(({ theme }) => ({
  transition: 'all 0.3s ease',
  ...(theme.palette.mode === 'dark' && {
    '&:hover': {
      boxShadow: '0 0 20px rgba(255, 165, 0, 0.1)',
      borderColor: 'rgba(255, 165, 0, 0.3)',
    },
  }),
}));

const GlowingChip = styled(Chip)(({ theme }) => ({
  transition: 'all 0.3s ease',
  ...(theme.palette.mode === 'dark' && {
    '&:hover': {
      boxShadow: '0 0 12px rgba(255, 165, 0, 0.3)',
    },
  }),
}));

interface ApplicationSelectorProps {
  applications: AIApplication[];
  selectedApp: string | null;
  onSelectionChange: (selectedApp: string) => void;
  onSubmit: () => void;
}

const ApplicationSelector: React.FC<ApplicationSelectorProps> = ({
  applications,
  selectedApp,
  onSelectionChange,
  onSubmit,
}) => {
  const theme = useTheme();
  const isDarkMode = theme.palette.mode === 'dark';
  const handleToggle = (appId: string) => {
    onSelectionChange(appId);
  };

  const handleSelectNone = () => {
    onSelectionChange(applications[0]?.id || '');
  };

  return (
    <Box>
      <Box sx={{ mb: 2, display: 'flex', gap: 1 }}>
        <Button size="small" variant="outlined" onClick={handleSelectNone}>
          Reset
        </Button>
        {selectedApp && (
          <Button size="small" variant="contained" onClick={onSubmit}>
            Submit
          </Button>
        )}
      </Box>

      <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', sm: '1fr 1fr', md: '1fr 1fr 1fr 1fr' }, gap: 2 }}>
        {applications.map((app) => {
          const isSelected = selectedApp === app.id;
          return (
            <Box key={app.id}>
              <GlowingCard
                sx={{
                  cursor: 'pointer',
                  border: isSelected ? 2 : 1,
                  borderColor: isSelected ? app.color : 'divider',
                  bgcolor: isSelected ? `${app.color}10` : 'background.paper',
                  transition: 'all 0.2s ease-in-out',
                  '&:hover': {
                    borderColor: app.color,
                    transform: 'translateY(-2px)',
                    boxShadow: isDarkMode ? `0 0 20px ${app.color}40` : 2,
                  },
                }}
                onClick={() => handleToggle(app.id)}
              >
                <CardContent sx={{ textAlign: 'center', py: 2 }}>
                  <Box
                    sx={{ 
                      mb: 1, 
                      display: 'flex', 
                      justifyContent: 'center', 
                      alignItems: 'center',
                      height: '48px'
                    }}
                  >
                    {typeof app.icon === 'string' ? (
                       <Typography variant="h3" sx={{ fontSize: '2rem' }}>
                         {app.icon}
                       </Typography>
                     ) : (
                       React.createElement(app.icon, { width: 32, height: 32, style: { color: app.color } })
                     )}
                  </Box>
                  <Typography
                    variant="h6"
                    sx={{ color: isSelected ? app.color : 'text.primary' }}
                  >
                    {app.displayName}
                  </Typography>
                  <FormControlLabel
                    control={
                      <Checkbox
                        checked={isSelected}
                        sx={{
                          color: app.color,
                          '&.Mui-checked': { color: app.color },
                        }}
                      />
                    }
                    label=""
                    sx={{ mt: 1, mb: 0 }}
                  />
                </CardContent>
              </GlowingCard>
            </Box>
          );
        })}
      </Box>

      {selectedApp && (
        <Box sx={{ mt: 2 }}>
          <Typography variant="body2" color="text.secondary" gutterBottom>
            Selected:
          </Typography>
          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
            {(() => {
              const app = applications.find(a => a.id === selectedApp);
              return app ? (
                <GlowingChip
                  icon={
                    typeof app.icon === 'string' ? (
                      <span style={{ fontSize: '14px' }}>{app.icon}</span>
                    ) : (
                      (() => {
                        const IconComponent = app.icon;
                        return <IconComponent width={16} height={16} style={{ color: 'white' }} />;
                      })()
                    )
                  }
                  label={app.displayName}
                  sx={{
                    bgcolor: app.color,
                    color: 'white',
                  }}
                />
              ) : null;
            })()}
          </Box>
        </Box>
      )}
    </Box>
  );
};

export default ApplicationSelector;