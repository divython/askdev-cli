package com.example.app;

public class MainActivityTest {
    public static void main(String[] args) {
        testNullString();
        testNonNullString();
    }

    public static void testNullString() {
        String s = null;
        System.out.print("Test null string: ");
        if (s != null) {
            System.out.println(s.length());
        } else {
            System.out.println("String is null");
        }
    }

    public static void testNonNullString() {
        String s = "hello";
        System.out.print("Test non-null string: ");
        if (s != null) {
            System.out.println(s.length());
        } else {
            System.out.println("String is null");
        }
    }
}
