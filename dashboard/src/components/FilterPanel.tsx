import React from 'react';
import {
  Box,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  TextField,
  Button,
  Typography,
  Divider,
  styled,
} from '@mui/material';
import { Clear, FilterList } from '@mui/icons-material';
import type { FilterOptions, AIApplication, MetricData } from '../types';

const GlowingButton = styled(Button)(({ theme }) => ({
  transition: 'all 0.3s ease',
  ...(theme.palette.mode === 'dark' && {
    '&:hover': {
      boxShadow: '0 0 15px rgba(255, 165, 0, 0.3)',
    },
  }),
}));

const GlowingTextField = styled(TextField)(({ theme }) => ({
  '& .MuiOutlinedInput-root': {
    ...(theme.palette.mode === 'dark' && {
      '&:hover .MuiOutlinedInput-notchedOutline': {
        borderColor: 'rgba(255, 165, 0, 0.5)',
        boxShadow: '0 0 8px rgba(255, 165, 0, 0.2)',
      },
      '&.Mui-focused .MuiOutlinedInput-notchedOutline': {
        borderColor: theme.palette.primary.main,
        boxShadow: '0 0 12px rgba(255, 165, 0, 0.3)',
      },
    }),
  },
}));

interface FilterPanelProps {
  filters: FilterOptions;
  onFiltersChange: (filters: FilterOptions) => void;
  applications: AIApplication[];
}

type SortableKeys = keyof MetricData;

const FilterPanel: React.FC<FilterPanelProps> = ({
  filters,
  onFiltersChange,
  applications,
}) => {
  // No theme-dependent logic needed here
  const sortableFields: { key: SortableKeys; label: string }[] = [
    { key: 'timestamp', label: 'Timestamp' },
    { key: 'responseTime', label: 'Response Time' },
    { key: 'requestCount', label: 'Request Count' },
    { key: 'successRate', label: 'Success Rate' },
    { key: 'errorRate', label: 'Error Rate' },
    { key: 'averageTokens', label: 'Average Tokens' },
    { key: 'cost', label: 'Cost' },
    { key: 'uptime', label: 'Uptime' },
  ];

  const handleApplicationChange = (applicationId: string) => {
    onFiltersChange({
      ...filters,
      application: applicationId || undefined,
    });
  };

  const handleDateRangeChange = (field: 'start' | 'end', value: string) => {
    const dateRange = filters.dateRange || { start: '', end: '' };
    onFiltersChange({
      ...filters,
      dateRange: {
        ...dateRange,
        [field]: value,
      },
    });
  };

  const handleSortChange = (field: 'sortBy' | 'sortOrder', value: string) => {
    onFiltersChange({
      ...filters,
      [field]: value || undefined,
    });
  };

  const handleClearFilters = () => {
    onFiltersChange({});
  };

  const hasActiveFilters = () => {
    return (
      filters.application ||
      filters.dateRange?.start ||
      filters.dateRange?.end ||
      filters.sortBy
    );
  };

  // Get default date range (last 7 days)
  const getDefaultDateRange = () => {
    const end = new Date();
    const start = new Date();
    start.setDate(start.getDate() - 7);
    
    return {
      start: start.toISOString().split('T')[0],
      end: end.toISOString().split('T')[0],
    };
  };

  const defaultDates = getDefaultDateRange();

  return (
    <Box>
      <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
        <FilterList sx={{ mr: 1 }} />
        <Typography variant="h6">Filters & Sorting</Typography>
        {hasActiveFilters() && (
          <GlowingButton
            startIcon={<Clear />}
            onClick={handleClearFilters}
            size="small"
            sx={{ ml: 'auto' }}
          >
            Clear All
          </GlowingButton>
        )}
      </Box>

      <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', sm: '1fr 1fr', md: '1fr 1fr 1fr 1fr' }, gap: 2 }}>
        {/* Application Filter */}
        <FormControl size="small">
          <InputLabel>Application</InputLabel>
          <Select
            value={filters.application || ''}
            label="Application"
            onChange={(e) => handleApplicationChange(e.target.value)}
          >
            <MenuItem value="">
              <em>Select Application</em>
            </MenuItem>
            {applications.map(app => (
              <MenuItem key={app.id} value={app.id}>
                <Box sx={{ display: 'inline-flex', alignItems: 'center', gap: 1 }}>
                  {typeof app.icon === 'string' ? (
                    <span style={{ fontSize: '16px' }}>{app.icon}</span>
                  ) : (
                    (() => {
                      const IconComponent = app.icon;
                      return <IconComponent width={16} height={16} />;
                    })()
                  )}
                  <span>{app.displayName}</span>
                </Box>
              </MenuItem>
            ))}
          </Select>
        </FormControl>

        {/* Date Range Start */}
        <GlowingTextField
          size="small"
          label="Start Date"
          type="date"
          value={filters.dateRange?.start || defaultDates.start}
          onChange={(e) => handleDateRangeChange('start', e.target.value)}
          InputLabelProps={{
            shrink: true,
          }}
        />

        {/* Date Range End */}
        <GlowingTextField
          size="small"
          label="End Date"
          type="date"
          value={filters.dateRange?.end || defaultDates.end}
          onChange={(e) => handleDateRangeChange('end', e.target.value)}
          InputLabelProps={{
            shrink: true,
          }}
        />

        {/* Sort By */}
        <FormControl size="small">
          <InputLabel>Sort By</InputLabel>
          <Select
            value={filters.sortBy || ''}
            label="Sort By"
            onChange={(e) => handleSortChange('sortBy', e.target.value)}
          >
            <MenuItem value="">
              <em>Default</em>
            </MenuItem>
            {sortableFields.map(field => (
              <MenuItem key={field.key} value={field.key}>
                {field.label}
              </MenuItem>
            ))}
          </Select>
        </FormControl>
      </Box>

      {/* Sort Order - Only show if sortBy is selected */}
      {filters.sortBy && (
        <Box sx={{ mt: 2 }}>
          <FormControl size="small" sx={{ minWidth: 120 }}>
            <InputLabel>Sort Order</InputLabel>
            <Select
              value={filters.sortOrder || 'desc'}
              label="Sort Order"
              onChange={(e) => handleSortChange('sortOrder', e.target.value)}
            >
              <MenuItem value="asc">Ascending</MenuItem>
              <MenuItem value="desc">Descending</MenuItem>
            </Select>
          </FormControl>
        </Box>
      )}

      <Divider sx={{ mt: 2 }} />

      {/* Active Filters Summary */}
      {hasActiveFilters() && (
        <Box sx={{ mt: 2 }}>
          <Typography variant="body2" color="text.secondary" gutterBottom>
            Active Filters:
          </Typography>
          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
            {filters.application && (
              <Box sx={{ bgcolor: 'primary.light', color: 'primary.contrastText', px: 1, py: 0.5, borderRadius: 1, fontSize: '0.75rem' }}>
                App: {applications.find(a => a.id === filters.application)?.displayName}
              </Box>
            )}
            {filters.dateRange?.start && (
              <Box sx={{ bgcolor: 'secondary.light', color: 'secondary.contrastText', px: 1, py: 0.5, borderRadius: 1, fontSize: '0.75rem' }}>
                From: {filters.dateRange.start}
              </Box>
            )}
            {filters.dateRange?.end && (
              <Box sx={{ bgcolor: 'secondary.light', color: 'secondary.contrastText', px: 1, py: 0.5, borderRadius: 1, fontSize: '0.75rem' }}>
                To: {filters.dateRange.end}
              </Box>
            )}
            {filters.sortBy && (
              <Box sx={{ bgcolor: 'info.light', color: 'info.contrastText', px: 1, py: 0.5, borderRadius: 1, fontSize: '0.75rem' }}>
                Sort: {sortableFields.find(f => f.key === filters.sortBy)?.label} ({filters.sortOrder || 'desc'})
              </Box>
            )}
          </Box>
        </Box>
      )}
    </Box>
  );
};

export default FilterPanel;