import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:septeria_personnel_mobile/main.dart';
import 'package:septeria_personnel_mobile/screens/login_screen.dart';

void main() {
  testWidgets('App renders login screen without active session', (WidgetTester tester) async {
    await tester.pumpWidget(const SepteriaPersonnelApp(initialSession: false));
    await tester.pumpAndSettle();

    expect(find.byType(LoginScreen), findsOneWidget);
    expect(find.text('SEPTERIA'), findsOneWidget);
    expect(find.text('Personnel Welfare & Support Portal'), findsOneWidget);
    expect(find.text('Sign In Securely'), findsOneWidget);
  });
}
