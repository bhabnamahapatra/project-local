import React from 'react';
import { Box, Dialog, DialogTitle, DialogContent, IconButton, Typography } from '@mui/material';
import { Close } from '@mui/icons-material';
import CopilotMetricsDashboard from './CopilotMetricsDashboard';

interface CopilotDashboardModalProps {
  open: boolean;
  onClose: () => void;
}

const CopilotDashboardModal: React.FC<CopilotDashboardModalProps> = ({
  open,
  onClose,
}) => {

  return (
    <Dialog
      open={open}
      onClose={onClose}
      maxWidth="xl"
      fullWidth
      PaperProps={{
        sx: {
          height: '90vh',
          maxHeight: '90vh',
        },
      }}
    >
      <DialogTitle>
        <Box display="flex" alignItems="center" justifyContent="space-between">
          <Box display="flex" alignItems="center" gap={2}>
            <img 
              src="https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png" 
              alt="GitHub" 
              style={{ width: 32, height: 32 }}
            />
            <Box>
              <Typography variant="h6" component="div" sx={{ fontWeight: 600 }}>
                GitHub Copilot Analytics Dashboard
              </Typography>
              <Typography variant="body2" sx={{ color: 'text.secondary' }}>
                Comprehensive metrics and insights for GitHub Copilot usage
              </Typography>
            </Box>
          </Box>
          <IconButton onClick={onClose}>
            <Close />
          </IconButton>
        </Box>
      </DialogTitle>
      
      <DialogContent dividers sx={{ p: 0 }}>
        <CopilotMetricsDashboard application="copilot" />
      </DialogContent>
    </Dialog>
  );
};

export default CopilotDashboardModal;