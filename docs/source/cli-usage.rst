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

Streams can be created with the `streamadd` command.
::

    ⇒  ouro streamadd new-stream

The remaining options for `streamadd` control the Access-Control List of the stream and are summarised below. Each option may be specified multiple times.

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

Replacing the ACL on an existing stream
---------------------------------------

The ACL can be completely rewritten by using the `set-acl` command. This command replaces the current ACL without any merge. Options are identical to :streamadd:`Creating a new stream`_
::

   ⇒  ouro streamadd new-stream -r devs -r ops -w ops


Granting permissions to an existing stream
------------------------------------------

The ACL can be extended by using the `grant` command. This command adds new entries into an existing ACL. Options are identical to `Creating a new stream`_
::

   ⇒  ouro streamadd new-stream -r devs -r ops -w ops

   ⇒  ouro grant new-stream -w devs

Removing permissions from an existing stream
---------------------------------------------

The ACL can be selectively revoked by using the `revoke` command. This command removes entries from an existing ACL. Options are identical to `Creating a new stream`_
::

   ⇒  ouro streamadd new-stream -r devs -r ops -w ops

   ⇒  ouro revoke new-stream -r devs


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
