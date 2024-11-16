import React from 'react';
import { Link } from "expo-router";
import { Text, View, Pressable } from "react-native";

export default function SignInScreen() {
  return (
    <View style={{ flex: 1, justifyContent: "center", alignItems: "center" }}>
      <Text>Sign In Screen</Text>
      <Pressable>
        <Link href="/navigation">Navigate</Link>
      </Pressable>
    </View>
  );
}
