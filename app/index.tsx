import React from 'react';
import { Link } from "expo-router";
import { Text, View, Pressable } from "react-native";

export default function SelectionScreen() {
  return (
    
    <View style={{ flex: 1, justifyContent: "center", alignItems: "center" }}>
      <Text>Selection Screen</Text>
      <Pressable>
        <Link href="/signIn">Sign In</Link>
        <Link href="/signUp">Sign Up</Link>
      </Pressable>
    </View>
  );
}
