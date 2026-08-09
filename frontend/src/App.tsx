import { createRouter, RouterProvider } from '@tanstack/react-router';
import { QueryClient } from '@tanstack/react-query';

import { Route as RootRoute } from './routes/__root';
import { Route as IndexRoute } from './routes/index';
import { Route as MarketRoute } from './routes/market';
import { Route as FarmerRoute } from './routes/farmer';
import { Route as SettingsRoute } from './routes/settings';

const routeTree = RootRoute.addChildren([
  IndexRoute,
  MarketRoute,
  FarmerRoute,
  SettingsRoute
]);

const queryClient = new QueryClient();

const router = createRouter({
  routeTree,
  context: {
    queryClient
  }
});

declare module '@tanstack/react-router' {
  interface Register {
    router: typeof router;
  }
}

export default function App() {
  return <RouterProvider router={router} />;
}
