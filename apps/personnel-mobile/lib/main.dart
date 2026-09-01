import 'package:flutter/material.dart';
import 'core/theme.dart';
import 'core/secure_storage.dart';
import 'screens/login_screen.dart';
import 'screens/home_screen.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  final storage = SecureStorageService();
  final hasSession = await storage.hasValidSession();
  runApp(SepteriaPersonnelApp(initialSession: hasSession));
}

class SepteriaPersonnelApp extends StatelessWidget {
  final bool initialSession;

  const SepteriaPersonnelApp({super.key, required this.initialSession});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'SEPTERIA Personnel',
      theme: AppTheme.darkTheme,
      debugShowCheckedModeBanner: false,
      home: initialSession ? const HomeScreen() : const LoginScreen(),
    );
  }
}
