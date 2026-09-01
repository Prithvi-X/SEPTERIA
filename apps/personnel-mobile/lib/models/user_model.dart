class UserModel {
  final String id;
  final String email;
  final String role;
  final String? force;
  final String? unitId;
  final bool isActive;

  UserModel({
    required this.id,
    required this.email,
    required this.role,
    this.force,
    this.unitId,
    required this.isActive,
  });

  factory UserModel.fromJson(Map<String, dynamic> json) {
    return UserModel(
      id: json['id'] as String,
      email: json['email'] as String,
      role: json['role'] as String,
      force: json['force'] as String?,
      unitId: json['unit_id'] as String?,
      isActive: json['is_active'] as bool? ?? true,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'email': email,
      'role': role,
      'force': force,
      'unit_id': unitId,
      'is_active': isActive,
    };
  }
}
