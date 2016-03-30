.. highlight:: console

Command-line Usage
==================

Ouroboros ships with a command-line client named *Ouro*. Ouro exposes all the functionality of Ouroboros for interactive use.

.. contents::
                        

Common Arguments
----------------

As well as the command-specific argments, Ouro requires some data about your eventstore instance. Each of these items can be specified as an environment variable, or on the command line.

+----------+-------------------------+-----------+---------------------------------------------------------+
| Option   | Env Var                 | Default   | Description                                             |
+==========+=========================+===========+=========================================================+
| authuser | ES_ADMIN_USER           | None      | The username ouro will use when contacting EventStore   |
+----------+-------------------------+-----------+---------------------------------------------------------+
| authpass | ES_ADMIN_PASS           | None      | The password ouro will use when contacting EventStore   |
+----------+-------------------------+-----------+---------------------------------------------------------+
| host     | ES_ADMIN_HOST           | localhost | The hostname or IP of the Eventstore instance to manage |
+----------+-------------------------+-----------+---------------------------------------------------------+
| port     | ES_ADMIN_PORT           | 2113      | The http interface port of the Eventstore instance      |
+----------+-------------------------+-----------+---------------------------------------------------------+
| no-ssl   | ES_ADMIN_DISABLE_SSL    | False     | Causes ouro to use http rather than https URIs.         |
+----------+-------------------------+-----------+---------------------------------------------------------+


.. _acl_options:

Specifying Access Control Lists
-------------------------------


Several of ouro's commands operate on access control lists. Each of these commands supports the following list of options. Each option may be specified multiple times.

+------------------+--------------+----------------------------------------------------------------------------------+
| Option           | Short-option | Description                                                                      |
+==================+==============+==================================================================================+
| --read           | -r           | Specifies a user or group who can read the stream                                |
+------------------+--------------+----------------------------------------------------------------------------------+
| --write          | -w           | Specifies a user or group who can write events to the stream                     |
+------------------+--------------+----------------------------------------------------------------------------------+
| --delete         | -d           | Specifies a user or group that can delete the stream                             |
+------------------+--------------+----------------------------------------------------------------------------------+
| --metadata-read  | -mr          | Specifies a user or group that can read the stream metadata, including the ACL   |
+------------------+--------------+----------------------------------------------------------------------------------+
| --metadata-write | -mw          | Specifies a user or group that can update the stream metadata, including the ACL |
+------------------+--------------+----------------------------------------------------------------------------------+


.. _acl_targetting:

Targetting Access Control Lists
-------------------------------


Commands that work with ACLs can be used with the ACL of a single stream, or with the default ACLs.

+------------------+----------------------------------------------------------------------------------+
| Option           | Description                                                                      |
+==================+==================================================================================+
| --stream foo     | Targets the ACL of an individual stream                                          |
+------------------+----------------------------------------------------------------------------------+
| --system         | Targets the default ACL for system-created streams                               |
+------------------+----------------------------------------------------------------------------------+
| --user           | Targets the default ACL for user-created streams                                 |
+------------------+----------------------------------------------------------------------------------+

Creating Users
--------------

The `useradd` command is responsible for creating users.
::

    ⇒  ouro useradd fred --password s00p3rs33krit

The password option is required, but can be entered interactively
::

    ⇒  ouro useradd giddy           
    Password: 

Users can be added to multiple groups during creation with the -g flag
::

    ⇒  ouro useradd fred -g devs -g ops -g $admins --password pw

The full name of the user can be specified with the -n flag. If not provided, the full name will default to the username.
::

    ⇒  ouro useradd fred -n "Fred Jarvis"


Deleting Users
--------------

The `userdel` command is responsible for deleting users.
::

    ⇒  ouro userdel fred


Creating a new stream
---------------------

Streams can be created with the `streamadd` command. You can specify an ACL for the new stream with the :ref:`ACL options <acl_options>`. Options that are not specified will fall back to the default acl.
::

    # Create a new stream, using the default ACL
    ⇒  ouro streamadd new-stream
        

    # Create a new stream, overriding the read options from the default acl
    ⇒  ouro streamadd new-stream -r devs -r ops -r qa


Replacing an ACL
----------------

An ACL can be completely rewritten by using the `set-acl` command. This command replaces the current ACL without any merge. You can modify an individual stream, or the default acls with the :ref:`targetting options <acl_targetting>`. Access control entries are specified with the :ref:`acl options <acl_options>`.
::

   ⇒  ouro set-acl --stream new-stream -r $all -w $admins -d $admins

   ⇒  ouro set-acl --user -r $all -w $admins -d $admins -d ops

   ⇒  ouro set-acl --system -r ops -r qa
   
Granting permissions to an existing stream
------------------------------------------

The ACL can be extended by using the `grant` command. This command adds new entries into an existing ACL. You can modify an individual stream, or the default acls with the :ref:`targetting options <acl_targetting>`. Access control entries are specified with the :ref:`acl options <acl_options>`.
::

   ⇒  ouro grant --stream new-stream -w devs

   ⇒  ouro grant --user -w devs

   ⇒  ouro grant --system -mw ops

Removing permissions from an existing stream
---------------------------------------------

The ACL can be selectively revoked by using the `revoke` command. This command removes entries from an existing ACL. You can modify an individual stream, or the default acls with the :ref:`targetting options <acl_targetting>`. Access control entries are specified with the :ref:`acl options <acl_options>`.
::


   ⇒  ouro revoke --stream new-stream -w devs

   ⇒  ouro revoke --user -w devs

   ⇒  ouro revoke --system -mw ops

Adding a user into a group
--------------------------

Users can be added to groups using either the `groupadd` command or the `usermod` command. Multiple groups can be added by repeating the `-g` flag.
::
    
   ⇒  ouro groupadd fred -g ops -g devs


   ⇒  ouro usermod fred -g ops -g devs

 
Removing a user from a group
-----------------------------

Users can be removed from groups using either the `groupdel` command or the `usermod` command. Multiple groups can be added by repeating the `-g` flag.
::
    
   ⇒  ouro groupdel fred -g ops -g devs

   ⇒  ouro usermod fred -r ops -r devs


Resetting a user's password
---------------------------

User passwords can be reset using the `usermod` command.
::

   ⇒  ouro usermod fred --password s00pers33krit

