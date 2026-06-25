class RBAC:
    def __init__(self, access_control):
        self.access_control = access_control

    def check(self, role, action, record_type):
        perms = self.access_control["roles"].get(role, [])
        if action not in perms:
            raise PermissionError(f"Role {role} cannot {action} {record_type}")
