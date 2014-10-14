# CHANGELOG

## 0.2

*2014-09-17*

- Extend permission system by adding user groups
- Code refactoring of modal windows
- Improved test coverage to 69%
- Bugfixes: sidebar, modal windows, user lists

#### Upgrading

After updating code to this version run `python manage.py migrate --merge` in application directory to update database schema.
Migrations will add 2 default groups to every department and assign all users to User groups.
It is *necessary* to manually assign Admin group to selected users, because this information is not migrated from v0.1.

## 0.1 Rocket launcher

*2014-08-18*

- organize applications and users in departments
- manage many servers using roles
- execute remote commands via SSH