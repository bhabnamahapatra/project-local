import React from 'react';
import { IconButton, Tooltip, Box } from '@mui/material';
import { LightMode, DarkMode } from '@mui/icons-material';
import { useTheme } from '../contexts/ThemeContext';
import { styled, keyframes } from '@mui/material/styles';

const glow = keyframes`
  0% {
    box-shadow: 0 0 5px rgba(255, 140, 0, 0.5);
  }
  50% {
    box-shadow: 0 0 20px rgba(255, 140, 0, 0.8), 0 0 30px rgba(255, 140, 0, 0.6);
  }
  100% {
    box-shadow: 0 0 5px rgba(255, 140, 0, 0.5);
  }
`;

const rotate = keyframes`
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
`;

const StyledToggleButton = styled(IconButton)(({ theme }) => ({
  position: 'relative',
  width: 48,
  height: 48,
  borderRadius: '50%',
  transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
  background: theme.palette.mode === 'dark' 
    ? 'linear-gradient(135deg, #FF8C00 0%, #FFA500 100%)'
    : 'linear-gradient(135deg, #FFD700 0%, #FFA500 100%)',
  border: `2px solid ${theme.palette.mode === 'dark' ? '#FF6600' : '#FF8C00'}`,
  boxShadow: theme.palette.mode === 'dark'
    ? '0 4px 15px rgba(255, 140, 0, 0.3)'
    : '0 4px 15px rgba(255, 165, 0, 0.2)',
  
  '&:hover': {
    transform: 'scale(1.1) rotate(10deg)',
    animation: `${glow} 2s ease-in-out infinite`,
    background: theme.palette.mode === 'dark'
      ? 'linear-gradient(135deg, #FFA500 0%, #FFD700 100%)'
      : 'linear-gradient(135deg, #FF8C00 0%, #FF6600 100%)',
  },
  
  '&:active': {
    transform: 'scale(0.95)',
    animation: `${rotate} 0.6s ease-in-out`,
  },
  
  '& .MuiSvgIcon-root': {
    fontSize: 24,
    color: theme.palette.mode === 'dark' ? '#000000' : '#ffffff',
    transition: 'all 0.3s ease',
    filter: 'drop-shadow(0 2px 4px rgba(0, 0, 0, 0.2))',
  },
  
  '&::before': {
    content: '""',
    position: 'absolute',
    top: -2,
    left: -2,
    right: -2,
    bottom: -2,
    borderRadius: '50%',
    background: theme.palette.mode === 'dark'
      ? 'linear-gradient(45deg, #FF8C00, #FFA500, #FFD700, #FF6600)'
      : 'linear-gradient(45deg, #FFD700, #FFA500, #FF8C00, #FF6600)',
    zIndex: -1,
    opacity: 0,
    transition: 'opacity 0.3s ease',
  },
  
  '&:hover::before': {
    opacity: 0.7,
    animation: `${rotate} 3s linear infinite`,
  },
}));

const ThemeToggle: React.FC = () => {
  const { mode, toggleTheme } = useTheme();

  return (
    <Box sx={{ position: 'relative' }}>
      <Tooltip 
        title={`Switch to ${mode === 'light' ? 'dark' : 'light'} mode`}
        placement="bottom"
      >
        <StyledToggleButton
          onClick={toggleTheme}
          aria-label={`Switch to ${mode === 'light' ? 'dark' : 'light'} mode`}
        >
          {mode === 'light' ? <DarkMode /> : <LightMode />}
        </StyledToggleButton>
      </Tooltip>
    </Box>
  );
};

export default ThemeToggle;