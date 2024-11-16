import React, {Component} from 'react';
import { Image, StyleSheet, Platform, Text, View, TouchableOpacity} from 'react-native';

const buttonWithBackground = props => {
    const content = (
        <View style = {[style.button, {backgroundColor:prop.color}]}>
            <Text style = {style.text}>{props.text}</Text>
        </View>
    );

    return <TouchableOpacity onPress={props.onPress}>{content}</TouchableOpacity>
}

const styles = StyleSheet.create({
    button:{
        padding: 16,
        width: 200,
        borderRadius: 24,
        alignItem: 'center'
    },
    text:{
        color:'white',
        font:20
    }

});

export default buttonWithBackground;

