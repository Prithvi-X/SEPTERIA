class PersonnelModel {
  final String id;
  final String personnelId;
  final String force;
  final String unitId;
  final String role;
  final String? rank;
  final String posting;
  final String status;

  PersonnelModel({
    required this.id,
    required this.personnelId,
    required this.force,
    required this.unitId,
    required this.role,
    this.rank,
    required this.posting,
    required this.status,
  });

  factory PersonnelModel.fromJson(Map<String, dynamic> json) {
    return PersonnelModel(
      id: json['id'] as String,
      personnelId: json['personnel_id'] as String,
      force: json['force'] as String,
      unitId: json['unit_id'] as String,
      role: json['role'] as String,
      rank: json['rank'] as String?,
      posting: json['posting'] as String,
      status: json['status'] as String? ?? 'ACTIVE',
    );
  }
}
