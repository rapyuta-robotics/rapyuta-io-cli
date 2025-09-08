;;; tramp-rio.el --- Tramp integration for HWIL devices -*- lexical-binding: t; -*-

;; Copyright (C) 2025 Rapyuta Robotics

;; Author: Ankit Gadiya <ankit.gadiya@rapyuta-robotics.com>
;; Version: 9.12.3
;; Package-Requires: ((emacs "29.1"))
;; Keywords: tools
;; URL: https://github.com/rapyuta-robotics/rapyuta-io-cli

;;; Commentary:

;; This package implements a Tramp backend for Hardware-in-the-loop devices in
;; rapyuta.io.

(require 'tramp)
(require 'rio)

(defconst tramp-rio-hwil-method "hwil"
  "Tramp method name to connect to HWIL machines.")

(defun tramp-rio-hwil--completion (&optional ignored)
  (let* ((output (rio--get-command-output '("hwil" "list")))
		 (devices (rio--parse-table-names output 1)))
	(mapcar (lambda (device) `(nil ,device)) devices)))

(defun tramp-rio-hwil-setup ()
  "Adds Hardware-in-the-loop device support in `tramp-mode'."
  (progn
	(add-to-list 'tramp-methods
				 `(,tramp-rio-hwil-method
				   (tramp-login-program ,rio-command)
				   (tramp-login-args (("hwil") ("ssh") ("%h")))
				   (tramp-remote-shell "/bin/bash")
				   (tramp-remote-shell-args ("-i" "-c"))))
	(tramp-set-completion-function tramp-rio-hwil-method '((tramp-rio-hwil--completion "")))))

(add-hook 'tramp-unload-hook
	  (lambda ()
	    (unload-feature 'tramp-rio 'force)))

(provide 'tramp-rio)
