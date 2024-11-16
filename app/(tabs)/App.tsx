// import * as React from 'react';
// import type {Node} from 'react';
// import { View, Text } from 'react-native';
// import { NavigationContainer } from '@react-navigation/native';
// import { createNativeStackNavigator } from '@react-navigation/native-stack';

// import NavigationScreen from '.app/screens/Navigation';
// import SelectionScreen from '.app/screens/Selection'; 
// import SignUpScreen from '.app/screens/SignUp';
// import SignInScreen from '.app/screens/SignIn'; 


// const App: () => Node = () => {
//   return (
//     <View>
//       <Text>Sign In</Text>
//     </View>
//   );
// }

// const RootStack = createNativeStackNavigator({
//   initialRouteName: 'Selection',
//   screens: {
//     Selection: {screen: SelectionScreen},
//     SignIn: {screen: SignInScreen},
//     SignUp: {screen: SignUpScreen}, 
//     Navigation: {screen: NavigationScreen}
//   },
// });

// const Navigation = createStaticNavigation(RootStack);

// export default function App() {
//   return <Navigation />;
// }