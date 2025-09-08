;;; rio.el --- Interface for rapyuta.io -*- lexical-binding: t; -*-

;; Copyright (C) 2025 Rapyuta Robotics

;; Author: Ankit Gadiya <ankit.gadiya@rapyuta-robotics.com>
;; Version: 9.12.3
;; Package-Requires: ((emacs "29.1") (transient "0.4.0"))
;; Keywords: tools
;; URL: https://github.com/rapyuta-robotics/rapyuta-io-cli

;;; Commentary:

;; This package provides a transient interface for the rapyuta.io CLI (rio). It
;; offers a convenient way to interact with rapyuta.io platfrom from Emacs.

;;; Code:

(require 'cl-lib)
(require 'transient)
(require 'tabulated-list)

;;; Customization

(defgroup rio nil
  "Rapyuta.io CLI interface."
  :group 'tools)

(defcustom rio-command (executable-find "rio")
  "Command to run rio CLI."
  :group 'rio
  :type '(choice (const "rio")
				 (string)))

;;; Helper functions

(defun rio--run-async-command (args &optional buffer-name)
  (let ((buffer (get-buffer-create (or buffer-name "*rio*")))
		(cmd (append `(,rio-command) args)))
	(async-shell-command (string-join cmd " ") buffer)))

(defun rio--run-command (args &optional buffer-name)
  "Run rio with ARGS and display output in BUFFER-NAME."
  (let ((buffer (get-buffer-create (or buffer-name "*rio*"))))
    (with-current-buffer buffer
      (let ((inhibit-read-only t))
        (erase-buffer))
      (apply #'call-process rio-command nil buffer t args)
      (goto-char (point-min)))
    (display-buffer buffer)))

(defun rio--get-command-output (args)
  "Get tabular output from rio ARGS as string."
  (with-temp-buffer
	(let ((retcode (apply #'call-process rio-command nil t nil args))
		  (output (buffer-string)))
	  (if (zerop retcode)
		  (string-trim output)
		(error output)))))

(defun rio--parse-table-names (output column)
  "Parse tabular OUTPUT and return names from COLUMN."
  (mapcar (lambda (line)
			(nth column line))
		  (rio--parse-list-output output)))

(defun rio--parse-list-output (output)
  "Parse a fixed-width table string OUTPUT, returning a list of rows of fields."
  (let* ((lines (split-string output "\n" t "[ \t\n\r]+"))
         (header (nth 0 lines))
		 (header-length (length header))
         (dashline (nth 1 lines))
         (rows (cddr lines))
         ;; Find column start/end indexes using the run of dashes in line 2
         (col-starts ())
         (col-ends ())
         (pos 0))
    ;; Parse column positions from dashline
    (while (string-match "-+" dashline pos)
	  (let ((begin (match-beginning 0))
	        (end   (match-end 0)))
		(push begin col-starts)
		(push end col-ends)
		(setq pos end)))
    (setq col-starts (nreverse col-starts))
    (setq col-ends   (nreverse (cons nil (cdr col-ends))))
    ;; Parse each row
    (mapcar
     (lambda (line)
	   (setq line-padded (string-pad line header-length))
	   (cl-mapcar
        (lambda (start end)
		  (string-trim (substring line-padded start end)))
        col-starts col-ends))
     rows)))

(defun rio--inspect-resource (resource-type name &optional inspect-cmd)
  "Display RESOURCE-TYPE NAME in an inspect buffer with appropriate mode."
  (let* ((buffer-name (format "*rio-%s-%s*" resource-type name))
		 (inspect-cmd (or inspect-cmd "inspect"))
         (output (rio--get-command-output (list resource-type inspect-cmd name))))
    (if output
        (let ((buffer (get-buffer-create buffer-name)))
          (with-current-buffer buffer
            (let ((inhibit-read-only t))
              (erase-buffer)
              (insert output)
              (goto-char (point-min))
              ;; Set appropriate mode based on content
              (cond
               ((string-match-p "apiVersion:" output) (yaml-ts-mode))
               ((string-match-p "^[[:space:]]*{" output) (json-ts-mode))
               (t (yaml-ts-mode))) ; Default to YAML
              (view-mode)))
          (display-buffer buffer))
      (message "Failed to inspect %s: %s" resource-type name))))

;;; Tabulated Resource List

(defun rio--parse-list-for-tabulated (output)
  "Parse tabular OUTPUT for use with tabulated-list-mode using separator line to determine columns."
  (when (and output (not (string-empty-p output)))
    (let* ((lines (split-string output "\n" t))
           (header-line (car lines))
           (separator-line (cadr lines))
           (data-lines (cddr lines)))

      ;; Parse column positions from separator line (dashes indicate column boundaries)
      (let ((positions '())
            (start 0)
            (in-dash-sequence nil))
        (dotimes (i (length separator-line))
          (let ((char (aref separator-line i)))
            (cond
             ;; Start of dash sequence
             ((and (eq char ?-) (not in-dash-sequence))
              (setq start i
                    in-dash-sequence t))
             ;; End of dash sequence (hit space while in dash sequence)
             ((and (eq char ?\ ) in-dash-sequence)
              (push (cons start (1- i)) positions)
              (setq in-dash-sequence nil)))))
        ;; Handle case where line ends with dashes
        (when in-dash-sequence
          (push (cons start (1- (length separator-line))) positions))
        (setq positions (reverse positions))

        ;; Extract headers based on column positions
        (let* ((headers (mapcar (lambda (pos)
                                 (let ((start (car pos))
                                       (end (cdr pos)))
                                   (string-trim
                                    (substring header-line start
                                              (min (1+ end) (length header-line))))))
                               positions))
               ;; Parse data entries using same column positions
               (rows (mapcar (lambda (line)
                              (let ((row-data (mapcar (lambda (pos)
                                                       (let ((start (car pos))
                                                             (end (cdr pos)))
                                                         (if (>= start (length line))
                                                             ""
                                                           (string-trim
                                                            (substring line start
                                                                      (min (1+ end) (length line)))))))
                                                     positions)))
                                ;; Return (ID . VECTOR) where ID is first column for tabulated-list
                                (list (car row-data) (vconcat row-data))))
                            data-lines)))
          (cons headers rows))))))

(defun rio--create-list-buffer (resource-type data)
  "Create a tabulated list buffer for RESOURCE-TYPE with DATA."
  (let ((buffer-name (format "*rio-%s-list*" resource-type))
        (column-names (car data))
        (rows (cdr data)))
    (with-current-buffer (get-buffer-create buffer-name)
      ;; Set up tabulated-list-mode
      (tabulated-list-mode)
      (setq tabulated-list-format
            (vconcat
             (mapcar (lambda (name)
                       (list name 20 t))
                     column-names)))
      (setq tabulated-list-entries rows)
      (tabulated-list-init-header)
      (tabulated-list-print)
      (goto-char (point-min))
      ;; Add local key bindings
      (local-set-key (kbd "RET") 'rio-list-inspect-at-point)
      (local-set-key (kbd "d") 'rio-list-delete-at-point)
      (local-set-key (kbd "g") 'revert-buffer)
      (setq-local rio-resource-type resource-type))
    (display-buffer buffer-name)))

(defvar-local rio-resource-type nil
  "Type of resource in the current buffer.")

(defun rio-list-inspect-at-point ()
  "Inspect the resource at point."
  (interactive)
  (when-let* ((id (tabulated-list-get-id)))
    (rio--inspect-resource rio-resource-type id)))

(defun rio-list-delete-at-point ()
  "Delete the resource at point."
  (interactive)
  (when-let* ((id (tabulated-list-get-id)))
    (when (yes-or-no-p (format "Delete %s '%s'? " rio-resource-type id))
	  (rio--run-async-command `(,rio-resource-type "delete" ,id "--silent"))
      (revert-buffer))))

;;; Completion functions

(defun rio--complete-devices-for-transient (&optional prompt initial history)
  "Completion function for device names in transient menus."
  (completing-read (or prompt "Device: ") (rio--complete-devices) nil nil initial history))

(defun rio--complete-secrets-for-transient (&optional prompt initial history)
  "Completion function for secret names in transient menus."
  (completing-read (or prompt "Secret: ") (rio--complete-secrets) nil nil initial history))

(defun rio--complete-deployments ()
  "Get list of deployment names for completion."
  (let ((output (rio--get-command-output '("deployment" "list"))))
    (rio--parse-table-names output 0)))

(defun rio--complete-devices ()
  "Get list of device names for completion."
  (let ((output (rio--get-command-output '("device" "list"))))
    (rio--parse-table-names output 1)))

(defun rio--complete-packages ()
  "Get list of package names for completion."
  (let ((output (rio--get-command-output '("package" "list"))))
    (rio--parse-table-names output 0)))

(defun rio--complete-networks ()
  "Get list of network names for completion."
  (let ((output (rio--get-command-output '("network" "list"))))
    (rio--parse-table-names output 1)))

(defun rio--complete-secrets ()
  "Get list of secret names for completion."
  (let ((output (rio--get-command-output '("secret" "list"))))
    (rio--parse-table-names output 1)))

(defun rio--complete-static-routes ()
  "Get list of static-route names for completion."
  (let ((output (rio--get-command-output '("static-route" "list"))))
    (rio--parse-table-names output 1)))

(defun rio--complete-disks ()
  "Get list of disk names for completion."
  (let ((output (rio--get-command-output '("disk" "list"))))
    (rio--parse-table-names output 1)))

(defun rio--complete-hwil ()
  "Get list of HWIL device names for completion."
  (let ((output (rio--get-command-output '("hwil" "list"))))
    (rio--parse-table-names output 1)))

(defun rio--complete-projects ()
  "Get list of project names for completion."
  (let ((output (rio--get-command-output '("project" "list"))))
    (rio--parse-table-names output 1)))

(defun rio--complete-usergroups ()
  "Get list of usergroup names for completion."
  (let ((output (rio--get-command-output '("usergroup" "list"))))
    (rio--parse-table-names output 1)))

(defun rio--complete-organizations ()
  "Get list of organization names for completion."
  (let ((output (rio--get-command-output '("organization" "list"))))
    (rio--parse-table-names output 0)))

(defun rio--complete-charts ()
  "Get list of chart names for completion."
  (let* ((output (rio--get-command-output '("chart" "list")))
		 (names (rio--parse-table-names output 0))
		 (versions (rio--parse-table-names output 1)))
	(cl-mapcar (lambda (name version)
				 (concat name ":" version))
			   names versions)))

(defun rio--complete-examples ()
  "Get list of manifest examples for completion."
  (let ((output (rio--get-command-output '("list-examples"))))
	(rio--parse-table-names output 0)))

;;; Readers

(defun rio-read-multiple-existing-file (prompt initial-input history)
  (completing-read-multiple "--value=" #'completion-file-name-table nil t))

;;; Context functions

(defun rio-context-view ()
  "View current CLI context."
  (interactive)
  (rio--run-command '("context" "view")))

;;; Auth functions

(defun rio-auth-login ()
  (interactive)
  (let* ((args (transient-args 'rio-auth-login-transient))
		 (silent (member "--silent" args)))
	(message (rio--get-command-output (append '("auth" "login" "--no-interactive") args)))
	(unless silent
	  (rio-organization-select)
	  (rio-project-select))))

(defun rio-auth-logout ()
  (interactive)
  (message (rio--get-command-output '("auth" "logout"))))

(defun rio-auth-status ()
  (interactive)
  (message (rio--get-command-output '("auth" "status"))))

(defun rio-auth-refresh-token ()
  (interactive)
  (let ((args (transient-args 'rio-auth-refresh-token-transient)))
	(message (rio--get-command-output (append '("auth" "refresh-token" "--no-interactive") args))))
  (transient-setup 'rio-transient))

(defun rio-auth-token ()
  (interactive)
  (let ((args (transient-args 'rio-auth-token-transient)))
	(message (rio--get-command-output (append '("auth" "token") args)))))

(defun rio-auth-environment ()
  (interactive)
  (let ((environment (read-string "Environment name: ")))
    (message (rio--get-command-output (list "auth" "environment" environment)))))

;;; Organization functions

(defun rio-organization-list ()
  (interactive)
  (let ((output (rio--get-command-output '("organization" "list"))))
    (when output
      (let ((data (rio--parse-list-for-tabulated output)))
        (rio--create-list-buffer "organization" data)))))

(defun rio-organization-select ()
  (interactive)
  (let ((org-name (completing-read "Select organization: "
                                   (rio--complete-organizations)
                                   nil t)))
    (message (rio--get-command-output (list "organization" "select" org-name))))
  (transient-setup 'rio-project-transient))

(defun rio-organization-inspect ()
  (interactive)
  (let ((org-name (completing-read "Inspect organization: "
                                      (rio--complete-organizations)
                                      nil t)))
    (rio--inspect-resource "organization" org-name)))

(defun rio-organization-users ()
  (interactive)
  (let ((output (rio--get-command-output '("organization" "users"))))
    (when output
      (let ((data (rio--parse-list-for-tabulated output)))
        (rio--create-list-buffer "users" data)))))

;;; Project functions

(defun rio-project-list ()
  (interactive)
  (let ((output (rio--get-command-output '("project" "list"))))
    (when output
      (let ((data (rio--parse-list-for-tabulated output)))
        (rio--create-list-buffer "project" data)))))

(defun rio-project-select ()
  (interactive)
  (let ((project-name (completing-read "Select project: "
                                       (rio--complete-projects)
                                       nil t)))
    (message (rio--get-command-output (list "project" "select" project-name)))))

(defun rio-project-inspect ()
  (interactive)
  (let ((project-name (completing-read "Inspect project: "
                                      (rio--complete-projects)
                                      nil t)))
    (rio--inspect-resource "project" project-name)))

(defun rio-project-create ()
  (interactive)
  (let ((project-name (read-string "Project name: ")))
    (message (rio--get-command-output (list "project" "create" project-name)))))

(defun rio-project-delete ()
  (interactive)
  (let ((project-name (completing-read "Delete project: "
									   (rio--complete-projects)
									   nil t)))
    (when (yes-or-no-p (format "Delete project '%s'? " project-name))
      (rio--run-async-command (list "project" "delete" "--silent" project-name)))))

(defun rio-project-features-vpn-enable ()
  "Enable VPN feature for a project."
  (interactive)
  (let ((args (transient-args 'rio-project-features-vpn-transient))
		(project-name (completing-read "Enable VPN for project: "
									   (rio--complete-projects)
									   nil t)))
	(rio--run-async-command (append `("project" "features" "vpn" ,project-name "true") args))))

(defun rio-project-features-vpn-disable ()
  "Disable VPN feature for a project."
  (interactive)
  (let ((project-name (completing-read "Disable VPN for project: "
                                      (rio--complete-projects)
                                      nil t)))
    (rio--run-async-command (list "project" "features" "vpn" project-name "false"))))

(defun rio-project-features-dockercache-enable ()
  "Enable Dockercache feature for a project."
  (interactive)
  (let ((args (transient-args 'rio-project-features-dockercache-transient))
		(project-name (completing-read "Enable Dockercache for project: "
									   (rio--complete-projects)
									   nil t)))
	(rio--run-async-command (append `("project" "features" "dockercache" ,project-name "true") args))))

(defun rio-project-features-dockercache-disable ()
  "Disable Dockercache feature for a project."
  (interactive)
  (let ((project-name (completing-read "Disable Dockercache for project: "
                                      (rio--complete-projects)
                                      nil t)))
    (rio--run-async-command (list "project" "features" "dockercache" project-name "false"))))

;;; Usergroup functions

(defun rio-usergroup-list ()
  "List usergroups."
  (interactive)
  (let ((output (rio--get-command-output '("usergroup" "list"))))
    (when output
      (let ((data (rio--parse-list-for-tabulated output)))
        (rio--create-list-buffer "usergroup" data)))))

(defun rio-usergroup-inspect ()
  "Inspect a usergroup."
  (interactive)
  (let ((org-name (completing-read "Inspect usergroup: "
                                      (rio--complete-usergroups)
                                      nil t)))
    (rio--inspect-resource "usergroup" org-name)))

(defun rio-usergroup-delete ()
  "Delete a usergroup."
  (interactive)
  (let ((usergroup-name (completing-read "Delete usergroup: "
                                      (rio--complete-usergroups)
                                      nil t)))
    (when (yes-or-no-p (format "Delete usergroup '%s'? " usergroup-name))
      (rio--run-async-command (list "usergroup" "delete" "--silent" usergroup-name)))))

;;; Device functions

(defun rio-device-list ()
  (interactive)
  (let ((output (rio--get-command-output '("device" "list"))))
    (when output
      (let ((data (rio--parse-list-for-tabulated output)))
        (rio--create-list-buffer "device" data)))))

(defun rio-device-inspect ()
  (interactive)
  (let ((device-name (completing-read "Inspect device: "
                                      (rio--complete-devices)
                                      nil t)))
    (rio--inspect-resource "device" device-name)))

(defun rio-device-delete ()
  (interactive)
  (let ((device-name (completing-read "Delete device: "
                                      (rio--complete-devices)
                                      nil t)))
    (when (yes-or-no-p (format "Delete device '%s'? " device-name))
      (rio--run-async-command (list "device" "delete" device-name)))))

;;; Deployment functions

(defun rio-deployment-list ()
  (interactive)
  (let ((output (rio--get-command-output '("deployment" "list"))))
    (when output
      (let ((data (rio--parse-list-for-tabulated output)))
        (rio--create-list-buffer "deployment" data)))))

(defun rio-deployment-inspect ()
  (interactive)
  (let ((deployment-name (completing-read "Inspect deployment: "
                                          (rio--complete-deployments)
                                          nil t)))
    (rio--inspect-resource "deployment" deployment-name)))

(defun rio-deployment-delete ()
  (interactive)
  (let ((deployment-name (completing-read "Delete deployment: "
                                          (rio--complete-deployments)
                                          nil t)))
    (when (yes-or-no-p (format "Delete deployment '%s'? " deployment-name))
      (rio--run-async-command (list "deployment" "delete" "--silent" deployment-name)))))

(defun rio-deployment-status ()
  (interactive)
  (let ((deployment-name (completing-read "Show status for deployment: "
                                          (rio--complete-deployments)
                                          nil t)))
    (rio--run-async-command (list "deployment" "status" deployment-name))))

(defun rio-deployment-logs ()
  (interactive)
  (let ((deployment-name (completing-read "Show logs for deployment: "
                                          (rio--complete-deployments)
                                          nil t)))
    (start-process "rio-logs" "*rio-logs*" rio-command "deployment" "logs" deployment-name)
    (display-buffer "*rio-logs*")))

;;; Package functions

(defun rio-package-list ()
  (interactive)
  (let ((output (rio--get-command-output '("package" "list"))))
    (when output
      (let ((data (rio--parse-list-for-tabulated output)))
        (rio--create-list-buffer "package" data)))))

(defun rio-package-inspect ()
  "Inspect a package."
  (interactive)
  (let ((package-name (completing-read "Inspect package: "
                                       (rio--complete-packages)
                                       nil t)))
    (rio--inspect-resource "package" package-name)))

(defun rio-package-delete ()
  "Delete a package."
  (interactive)
  (let ((package-name (completing-read "Delete package: "
                                       (rio--complete-packages)
                                       nil t)))
    (when (yes-or-no-p (format "Delete package '%s'? " package-name))
      (rio--run-async-command (list "package" "delete" "--silent" package-name)))))

;;; Network functions

(defun rio-network-list ()
  "List networks."
  (interactive)
  (let ((output (rio--get-command-output '("network" "list"))))
    (when output
      (let ((data (rio--parse-list-for-tabulated output)))
        (rio--create-list-buffer "network" data)))))

(defun rio-network-inspect ()
  "Inspect a network."
  (interactive)
  (let ((network-name (completing-read "Inspect network: "
                                       (rio--complete-networks)
                                       nil t)))
    (rio--inspect-resource "network" network-name)))

(defun rio-network-delete ()
  "Delete a network."
  (interactive)
  (let ((network-name (completing-read "Delete network: "
                                       (rio--complete-networks)
                                       nil t)))
    (when (yes-or-no-p (format "Delete network '%s'? " network-name))
      (rio--run-async-command (list "network" "delete" "--force" network-name)))))

;;; Secret functions

(defun rio-secret-list ()
  "List secrets."
  (interactive)
  (let ((output (rio--get-command-output '("secret" "list"))))
    (when output
      (let ((data (rio--parse-list-for-tabulated output)))
        (rio--create-list-buffer "secret" data)))))

(defun rio-secret-inspect ()
  "Inspect a secret."
  (interactive)
  (let ((secret-name (completing-read "Inspect secret: "
                                      (rio--complete-secrets)
                                      nil t)))
    (rio--inspect-resource "secret" secret-name)))

(defun rio-secret-delete ()
  "Delete a secret."
  (interactive)
  (let ((secret-name (completing-read "Delete secret: "
                                      (rio--complete-secrets)
                                      nil t)))
    (when (yes-or-no-p (format "Delete secret '%s'? " secret-name))
      (rio--run-async-command (list "secret" "delete" "--silent" secret-name)))))

;;; StaticRoute functions

(defun rio-static-route-list ()
  "List static-routes."
  (interactive)
  (let ((output (rio--get-command-output '("static-route" "list"))))
    (when output
      (let ((data (rio--parse-list-for-tabulated output)))
        (rio--create-list-buffer "static-route" data)))))

(defun rio-static-route-inspect ()
  "Inspect a static-route."
  (interactive)
  (let ((static-route-name (completing-read "Inspect static-route: "
                                      (rio--complete-static-routes)
                                      nil t)))
    (rio--inspect-resource "static-route" static-route-name)))

(defun rio-static-route-delete ()
  "Delete a static-route."
  (interactive)
  (let ((static-route-name (completing-read "Delete static-route: "
                                      (rio--complete-static-routes)
                                      nil t)))
    (when (yes-or-no-p (format "Delete static-route '%s'? " static-route-name))
      (rio--run-async-command (list "static-route" "delete" "--silent" static-route-name)))))

;;; Disk functions

(defun rio-disk-list ()
  "List disks."
  (interactive)
  (let ((output (rio--get-command-output '("disk" "list"))))
    (when output
      (let ((data (rio--parse-list-for-tabulated output)))
        (rio--create-list-buffer "disk" data)))))

(defun rio-disk-inspect ()
  "Inspect a disk."
  (interactive)
  (let ((disk-name (completing-read "Inspect disk: "
                                    (rio--complete-disks)
                                    nil t)))
    (rio--inspect-resource "disk" disk-name)))

(defun rio-disk-delete ()
  "Delete a disk."
  (interactive)
  (let ((disk-name (completing-read "Delete disk: "
                                    (rio--complete-disks)
                                    nil t)))
    (when (yes-or-no-p (format "Delete disk '%s'? " disk-name))
      (rio--run-async-command (list "disk" "delete" "--force" disk-name)))))

;;; HWIL functions

(defun rio-hwil-list ()
  "List HWIL Devices."
  (interactive)
  (let ((output (rio--get-command-output '("hwil" "list"))))
    (when output
      (let ((data (rio--parse-list-for-tabulated output)))
        (rio--create-list-buffer "hwil" data)))))

(defun rio-hwil-inspect ()
  "Inspect a HWIL Device."
  (interactive)
  (let ((device-name (completing-read "Inspect HWIL: "
                                    (rio--complete-hwil)
                                    nil t)))
    (rio--inspect-resource "hwil" device-name)))

(defun rio-hwil-ssh ()
  "Inspect a HWIL Device."
  (interactive)
  (let* ((device-name (completing-read "SSH HWIL: "
                                       (rio--complete-hwil)
                                       nil t))
		 (default-directory (format "/hwil:%s|sudo::" device-name)))
	(eshell)))

;;; VPN functions

(defun rio-vpn-connect ()
  (interactive)
  (let ((args (transient-args 'rio-vpn-connect-transient)))
	(rio--run-async-command (append '("vpn" "connect" "--silent") args))))

(defun rio-vpn-disconnect ()
  (interactive)
  (rio--run-async-command '("vpn" "disconnect")))

(defun rio-vpn-flush ()
  (interactive)
  (rio--run-async-command '("vpn" "flush")))

(defun rio-vpn-status ()
  "Show VPN status."
  (interactive)
  (rio--run-async-command '("vpn" "status")))

;;; Apply/Delete functions

(defun rio--read-manifest-file (&optional prompt)
  "Read a manifest file name with filtering for YAML/JSON files."
  (expand-file-name (read-file-name (or prompt "Manifest file: ") nil nil t nil
									(lambda (name)
									  (or (file-directory-p name)
										  (string-match-p "\\.\\(ya?ml\\|json\\)\\'" name))))))

(defun rio--read-manifest-directory ()
  "Read a directory containing manifest files."
  (expand-file-name (read-directory-name "Manifest directory: ")))

(defun rio-apply ()
  "Apply one or more manifest files."
  (interactive)
  (let* ((args (transient-args 'rio-apply-transient))
		 (manifests (completing-read-multiple "Manifests: " #'completion-file-name-table nil t))
		 (command (append '("apply" "--silent") args manifests)))
	(rio--run-async-command command)))

(defun rio-delete ()
  "Delete one or more manifest files."
  (interactive)
  (let* ((args (transient-args 'rio-delete-transient))
		 (manifests (completing-read-multiple "Manifests: " #'completion-file-name-table nil t))
		 (command (append '("delete" "--silent") args manifests)))
	(rio--run-async-command command)))

(defun rio-template ()
  "Render manifest templates without applying."
  (interactive)
  (let* ((args (transient-args 'rio-template-transient))
		 (manifests (completing-read-multiple "Manifests: " #'completion-file-name-table nil t))
		 (command (append '("template") args manifests)))
	(rio--run-command command "*rio-template*")))

(defun rio-explain ()
  "Generate sample manifests."
  (interactive)
  (let* ((example (completing-read "Example: "
								   (rio--complete-examples)
								   nil t))
		 (command (list "explain" example)))
	(rio--run-command command "*rio-explain*")))

;;; Chart functions

(defun rio-chart-list ()
  "List charts."
  (interactive)
  (let ((output (rio--get-command-output '("chart" "list"))))
    (when output
      (let ((data (rio--parse-list-for-tabulated output)))
        (rio--create-list-buffer "chart" data)))))

(defun rio-chart-inspect ()
  "Inspect a chart."
  (interactive)
  (let ((chart-name (completing-read "Inspect chart: "
                                    (rio--complete-charts)
                                    nil t)))
    (rio--inspect-resource "chart" chart-name "info")))

(defun rio-chart-apply ()
  "Apply a chart."
  (interactive)
  (let* ((chart-name (completing-read "Chart: "
									  (rio--complete-charts)
									  nil t))
		 (args (transient-args 'rio-chart-apply-transient))
		 (command (append '("chart" "apply" "--silent") args `(,chart-name))))
	(rio--run-async-command command)))

(defun rio-chart-delete ()
  "Delete a chart."
  (interactive)
  (let* ((chart-name (completing-read "Chart: "
									  (rio--complete-charts)
									  nil t))
		 (args (transient-args 'rio-chart-delete-transient))
		 (command (append '("chart" "delete" "--silent") args `(,chart-name))))
	(rio--run-async-command command)))

;;; Transient definitions

(transient-define-prefix rio-auth-login-transient ()
  ["rio auth login\n"
   ["Options"
    ("-e" "Email of the rapyuta.io account" "--email=" :reader read-string)
    ("-p" "Password for the rapyuta.io account" "--password=" :reader read-passwd)
    ("-t" "Login with auth token only" "--auth-token=" :reader read-string)
    ("-s" "Make login interactive" "--silent" :reader read-string)]]
  [("l" "Login" rio-auth-login)])

(transient-define-prefix rio-auth-refresh-token-transient ()
  ["rio auth refresh-token\n"
   ["Options"
    ("-p" "Password for the rapyuta.io account" "--password=" :reader read-passwd)]]
  [("r" "Refresh" rio-auth-refresh-token)])

(transient-define-prefix rio-auth-token-transient ()
  ["rio auth token\n"
   ["Options"
    ("-e" "Email" "--email=" :reader read-string)
    ("-p" "Password" "--password=" :reader read-passwd)]]
  [("t" "Generate Token" rio-auth-token)])

(transient-define-prefix rio-auth-transient ()
  ["rio auth\n"
   ("l" "Login" rio-auth-login-transient)
   ("o" "Logout" rio-auth-logout)
   ("r" "Refresh Token" rio-auth-refresh-token-transient)
   ("s" "Status" rio-auth-status)
   ("t" "Generate Token" rio-auth-token-transient)
   ("e" "Set Environment" rio-auth-environment :transient t)])

(transient-define-prefix rio-organization-transient ()
  ["rio organization\n"
   ("i" "Inspect" rio-organization-inspect)
   ("l" "List" rio-organization-list)
   ("s" "Set" rio-organization-select)
   ("u" "List Users" rio-organization-users)])

(transient-define-prefix rio-project-features-vpn-transient ()
  ["rio project features vpn\n"
   ["Options"
    ("-s" "Subnet ranges for the project" "--subnets=" :reader read-string)]]
   [["Actions"
    ("e" "Enable" rio-project-features-vpn-enable)
    ("d" "Disable" rio-project-features-vpn-disable)]])

(transient-define-prefix rio-project-features-dockercache-transient ()
  "Project Dockercache features management."
  ["rio project features dockercache\n"
   ["Options"
    ("-d" "Name of the device for docker-cache proxy" "--proxy-device=" :reader rio--complete-devices-for-transient)
    ("-i" "Name of the network interface for docker-cache proxy" "--proxy-interface=" :reader read-string)
    ("-u" "URL for the upstream docker registry" "--registry-url=" :reader read-string)
    ("-s" "Name of the secret for upstream docker registry" "--registry-secret=" :reader rio--complete-secrets-for-transient)
    ("-D" "Registry data directory path" "--data-directory=" :reader read-string)]]
  [["Actions"
    ("e" "Enable" rio-project-features-dockercache-enable)
    ("d" "Disable" rio-project-features-dockercache-disable)]])

(transient-define-prefix rio-project-features-transient ()
  "Project features management."
  ["rio project features\n"
   ("d" "Toggle DockerCache on a project." rio-project-features-dockercache-transient)
   ("v" "Toggle VPN on a project." rio-project-features-vpn-transient)])

(transient-define-prefix rio-project-transient ()
  "Rapyuta.io CLI project management."
  ["rio project\n"
   ("c" "Create" rio-project-create)
   ("d" "Delete" rio-project-delete)
   ("f" "Features" rio-project-features-transient)
   ("i" "Inspect" rio-project-inspect)
   ("l" "List" rio-project-list)
   ("s" "Set" rio-project-select)])

(transient-define-prefix rio-usergroup-transient ()
  "Rapyuta.io CLI usergroup management."
  ["rio usergroup\n"
   ("d" "Delete" rio-usergroup-delete)
   ("i" "Inspect" rio-usergroup-inspect)
   ("l" "List" rio-usergroup-list)])

(transient-define-prefix rio-device-transient ()
  "Rapyuta.io CLI device management."
  ["rio device\n"
   ("l" "List" rio-device-list)
   ("i" "Inspect" rio-device-inspect)
   ("d" "Delete" rio-device-delete)])

(transient-define-prefix rio-deployment-transient ()
  "Rapyuta.io CLI deployment management."
  ["rio deployment\n"
   ("l" "List" rio-deployment-list)
   ("i" "Inspect" rio-deployment-inspect)
   ("d" "Delete" rio-deployment-delete)
   ("s" "Status" rio-deployment-status)
   ("L" "Logs" rio-deployment-logs)])

(transient-define-prefix rio-package-transient ()
  "Rapyuta.io CLI package management."
  ["rio package\n"
   ("l" "List" rio-package-list)
   ("i" "Inspect" rio-package-inspect)
   ("d" "Delete" rio-package-delete)])

(transient-define-prefix rio-network-transient ()
  "Rapyuta.io CLI network management."
  ["rio network\n"
   ("l" "List" rio-network-list)
   ("i" "Inspect" rio-network-inspect)
   ("d" "Delete" rio-network-delete)])

(transient-define-prefix rio-secret-transient ()
  "Rapyuta.io CLI secret management."
  ["rio secret\n"
   ("l" "List" rio-secret-list)
   ("i" "Inspect" rio-secret-inspect)
   ("d" "Delete" rio-secret-delete)])

(transient-define-prefix rio-static-route-transient ()
  "Rapyuta.io CLI static-route management."
  ["rio static-route\n"
   ("l" "List" rio-static-route-list)
   ("i" "Inspect" rio-static-route-inspect)
   ("d" "Delete" rio-static-route-delete)])

(transient-define-prefix rio-disk-transient ()
  "Rapyuta.io CLI disk management."
  ["rio disk\n"
   ("l" "List" rio-disk-list)
   ("i" "Inspect" rio-disk-inspect)
   ("d" "Delete" rio-disk-delete)])

(transient-define-prefix rio-hwil-transient ()
  "Rapyuta.io CLI HWIL management."
  ["rio hwil\n"
   ("l" "List" rio-hwil-list)
   ("i" "Inspect" rio-hwil-inspect)
   ("s" "SSH" rio-hwil-ssh)])

(transient-define-prefix rio-vpn-connect-transient ()
  ["rio vpn connect\n"
   ["Options"
	("-u" "Update hosts file with VPN peers to allow access to them by hostname" "--update-hosts")]]
   ["Actions"
	("c" "Connect" rio-vpn-connect)])

(transient-define-prefix rio-vpn-transient ()
  "Rapyuta.io CLI VPN management."
  ;; FIXME: Figure out a way to call the commands from root.
  ["rio vpn\n"
   ("c" "Connect" rio-vpn-connect-transient)
   ("d" "Disconnect" rio-vpn-disconnect)
   ("f" "Flush configuration" rio-vpn-flush)
   ("s" "Status" rio-vpn-status)])

(transient-define-prefix rio-apply-transient ()
  "Apply rapyuta.io manifests."
  ["rio apply\n"
   ["Template Support"
    ("-v" "Values file" "--values="
     :reader rio-read-multiple-existing-file
     :multi-value repeat)
    ("-s" "Secrets file" "--secrets="
     :reader rio-read-multiple-existing-file
     :multi-value repeat)]
   ["Performance"
    ("-w" "Workers" "--workers="
     :reader transient-read-number-N+)
    ("-c" "Retry count" "--retry-count="
     :reader transient-read-number-N+)
    ("-i" "Retry interval" "--retry-interval="
     :reader transient-read-number-N+)]
   ["Options"
    ("-D" "Dry run" "--dryrun")
    ("-g" "Show dependency graph" "--show-graph")
    ("-r" "Recreate existing resources" "--recreate")]]
  [["Manifests"
    ("m" "Manifest" rio-apply)]])

(transient-define-prefix rio-delete-transient ()
  "Delete rapyuta.io resources via manifests."
  ["rio delete\n"
   ["Template Support"
    ("-v" "Values file" "--values="
     :reader rio-read-multiple-existing-file
     :multi-value repeat)
    ("-s" "Secrets file" "--secrets="
     :reader rio-read-multiple-existing-file
     :multi-value repeat)]
   ["Performance"
    ("-w" "Workers" "--workers="
     :reader transient-read-number-N+)
    ("-c" "Retry count" "--retry-count="
     :reader transient-read-number-N+)
    ("-i" "Retry interval" "--retry-interval="
     :reader transient-read-number-N+)]
   ["Options"
    ("-D" "Dry run" "--dryrun")]]
   ["Manifests"
    ("m" "Manifests" rio-delete)])

(transient-define-prefix rio-template-transient ()
  "Render manifest templates without applying."
  ["rio template\n"
   ["Template Support"
    ("-v" "Values file" "--values="
     :reader rio-read-multiple-existing-file
     :multi-value repeat)
    ("-s" "Secrets file" "--secrets="
     :reader rio-read-multiple-existing-file
     :multi-value repeat)]]
   ["Manifests"
    ("m" "Manifests" rio-template)])

(transient-define-prefix rio-chart-apply-transient ()
  "Apply rapyuta.io manifests."
  ["rio chart apply\n"
   ["Template Support"
    ("-v" "Values file" "--values="
     :reader rio-read-multiple-existing-file
     :multi-value repeat)
    ("-s" "Secrets file" "--secrets="
     :reader rio-read-multiple-existing-file
     :multi-value repeat)]
   ["Performance"
    ("-w" "Workers" "--workers="
     :reader transient-read-number-N+)
    ("-c" "Retry count" "--retry-count="
     :reader transient-read-number-N+)
    ("-i" "Retry interval" "--retry-interval="
     :reader transient-read-number-N+)]
   ["Options"
    ("-D" "Dry run" "--dryrun")
    ("-r" "Recreate existing resources" "--recreate")]]
  [["Operation"
    ("m" "Apply" rio-chart-apply)]])

(transient-define-prefix rio-chart-delete-transient ()
  "Apply rapyuta.io manifests."
  ["rio chart delete\n"
   ["Template Support"
    ("-v" "Values file" "--values="
     :reader rio-read-multiple-existing-file
     :multi-value repeat)
    ("-s" "Secrets file" "--secrets="
     :reader rio-read-multiple-existing-file
     :multi-value repeat)]
   ["Performance"
    ("-w" "Workers" "--workers="
     :reader transient-read-number-N+)
    ("-c" "Retry count" "--retry-count="
     :reader transient-read-number-N+)
    ("-i" "Retry interval" "--retry-interval="
     :reader transient-read-number-N+)]
   ["Options"
    ("-D" "Dry run" "--dryrun")]]
  [["Operation"
    ("m" "Delete" rio-chart-delete)]])

(transient-define-prefix rio-chart-transient ()
  "Rapyuta.io Charts management."
  ["rio chart\n"
   ("l" "List" rio-chart-list)
   ("i" "Inspect" rio-chart-inspect)
   ("+" "Apply" rio-chart-apply-transient)
   ("-" "Delete" rio-chart-delete-transient)])

;;;###autoload
(transient-define-prefix rio-transient ()
  "Rapyuta.io CLI transient interface."
  ["rapyuta.io Transient\n"
   ["Configuration"
	("a" "Auth" rio-auth-transient)
	("c" "Context" rio-context-view)]
   ["Organizational Units"
	("o" "Organization" rio-organization-transient)
	("p" "Project" rio-project-transient)
	("u" "Usergroup" rio-usergroup-transient)]
   ["Features"
	 ("v" "VPN" rio-vpn-transient)]
   ["Operations"
	("+" "Apply" rio-apply-transient)
	("-" "Delete" rio-delete-transient)
	("t" "Template" rio-template-transient)
	("e" "Explain" rio-explain)
	("C" "Charts" rio-chart-transient)]]
  ["Resources"
   [("P" "Package" rio-package-transient)
	("d" "Deployment" rio-deployment-transient)
	("D" "Device" rio-device-transient)
	("k" "Disk" rio-disk-transient)]
   [("n" "Network" rio-network-transient)
	("s" "Secret" rio-secret-transient)
	("S" "Static Route" rio-static-route-transient)]
   [("h" "Hardware-in-the-Loop" rio-hwil-transient)]])

(provide 'rio)
;;; rio.el ends here
