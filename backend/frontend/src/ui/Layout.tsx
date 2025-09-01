import { AppBar, Box, Container, Link as MuiLink, Toolbar, Typography } from '@mui/material';
import { Link, Outlet } from 'react-router-dom';

export function Layout() {
  return (
    <Box sx={{ minHeight: '100vh', bgcolor: '#f6f7fb' }}>
      <AppBar position="static" color="primary">
        <Toolbar>
          <Typography variant="h6" sx={{ flexGrow: 1 }}>
            Empresa Admin
          </Typography>
          <MuiLink component={Link} color="inherit" to="/" sx={{ mr: 2 }}>
            Dashboard
          </MuiLink>
          <MuiLink component={Link} color="inherit" to="/receber">
            Contas a Receber
          </MuiLink>
          <MuiLink component={Link} color="inherit" to="/pagar" sx={{ ml: 2 }}>
            Contas a Pagar
          </MuiLink>
        </Toolbar>
      </AppBar>
      <Container maxWidth="xl" sx={{ py: 3 }}>
        <Outlet />
      </Container>
    </Box>
  );
}
