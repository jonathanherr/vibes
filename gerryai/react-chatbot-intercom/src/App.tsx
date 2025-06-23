import React from 'react';
import { BrowserRouter as Router, Route, Switch, Redirect } from 'react-router-dom';
import Header from './components/common/Header';
import Layout from './components/common/Layout';
import ChatContainer from './components/Chat/ChatContainer';
import HUDContainer from './components/HUD/HUDContainer';
import IntercomPanel from './components/Intercom/IntercomPanel';
import LLMTest from './components/Debug/LLMTest';

const App = () => {
  return (
    <Router>
      <Header />
      <Layout>
        <Switch>
          <Route path="/chat" component={ChatContainer} />
          <Route path="/hud" component={HUDContainer} />
          <Route path="/intercom" component={IntercomPanel} />
          <Route path="/" exact>
            <Redirect to="/chat" />
          </Route>
        </Switch>
      </Layout>
    </Router>
  );
};

export default App;