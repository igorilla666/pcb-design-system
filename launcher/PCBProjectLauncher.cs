// SPDX-License-Identifier: Apache-2.0
// Copyright 2026 igorilla666

using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Drawing;
using System.IO;
using System.Reflection;
using System.Text;
using System.Text.RegularExpressions;
using System.Threading.Tasks;
using System.Windows.Forms;

[assembly: AssemblyTitle("PCB Project Launcher")]
[assembly: AssemblyProduct("PCB Design System")]
[assembly: AssemblyDescription("Multi-agent PCB project launcher. Licensed under Apache-2.0.")]
[assembly: AssemblyCompany("pcb-design-system contributors")]
[assembly: AssemblyCopyright("Copyright © 2026 igorilla666")]
[assembly: AssemblyVersion("0.4.2.0")]
[assembly: AssemblyFileVersion("0.4.2.0")]
[assembly: AssemblyInformationalVersion("0.4.2")]
[assembly: AssemblyMetadata("License", "Apache-2.0")]

namespace PcbDesignSystem
{
    internal static class Program
    {
        [STAThread]
        private static void Main(string[] args)
        {
            if (args.Length > 0 && args[0] == "--diagnostics")
            {
                string report = args.Length > 1
                    ? args[1]
                    : Path.Combine(Path.GetTempPath(), "pcb-project-launcher-diagnostics.txt");
                File.WriteAllLines(report, LauncherSupport.Diagnostics(), Encoding.UTF8);
                return;
            }

            Application.EnableVisualStyles();
            Application.SetCompatibleTextRenderingDefault(false);
            Application.Run(new LauncherForm());
        }
    }

    internal sealed class ProjectRequest
    {
        public string Agent;
        public string Name;
        public string Repository;
        public string Target;
        public string GitName;
        public string GitEmail;
        public bool Public;
        public bool CreateGitHub;
        public bool OpenAgent;
    }

    internal sealed class CommandResult
    {
        public int ExitCode;
        public string Output;
    }

    internal static class LauncherSupport
    {
        public static string Slugify(string value)
        {
            string normalized = value.Trim().ToLowerInvariant();
            normalized = Regex.Replace(normalized, @"[^a-z0-9]+", "-");
            return normalized.Trim('-');
        }

        public static string FindNewProjectScript()
        {
            string home = Environment.GetFolderPath(Environment.SpecialFolder.UserProfile);
            string baseDirectory = AppDomain.CurrentDomain.BaseDirectory;
            string[] candidates =
            {
                Path.Combine(baseDirectory, "scripts", "new_project.py"),
                Path.GetFullPath(Path.Combine(baseDirectory, "..", "scripts", "new_project.py")),
                Path.Combine(home, ".codex", "skills", "pcb-design-system", "scripts", "new_project.py"),
                Path.Combine(home, ".gemini", "config", "skills", "pcb-design-system", "scripts", "new_project.py"),
                Path.Combine(home, ".gemini", "skills", "pcb-design-system", "scripts", "new_project.py"),
                Path.Combine(home, ".claude", "skills", "pcb-design-system", "scripts", "new_project.py")
            };

            foreach (string candidate in candidates)
            {
                if (File.Exists(candidate))
                    return Path.GetFullPath(candidate);
            }
            return null;
        }

        public static string FindExecutable(string name, params string[] additionalCandidates)
        {
            string pathValue = Environment.GetEnvironmentVariable("PATH") ?? string.Empty;
            foreach (string directory in pathValue.Split(Path.PathSeparator))
            {
                if (string.IsNullOrWhiteSpace(directory))
                    continue;
                try
                {
                    string candidate = Path.Combine(directory.Trim(), name);
                    if (File.Exists(candidate))
                        return candidate;
                }
                catch (ArgumentException)
                {
                }
            }

            foreach (string candidate in additionalCandidates)
            {
                if (!string.IsNullOrWhiteSpace(candidate) && File.Exists(candidate))
                    return candidate;
            }
            return null;
        }

        public static string FindPython()
        {
            string local = Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData);
            return FindExecutable(
                "python.exe",
                Path.Combine(local, "Microsoft", "WindowsApps", "python.exe"));
        }

        public static string FindAntigravity()
        {
            string local = Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData);
            string programFiles = Environment.GetFolderPath(Environment.SpecialFolder.ProgramFiles);
            return FindExecutable(
                "Antigravity.exe",
                Path.Combine(local, "Programs", "antigravity", "Antigravity.exe"),
                Path.Combine(local, "Programs", "Antigravity IDE", "Antigravity IDE.exe"),
                Path.Combine(programFiles, "Antigravity", "Antigravity.exe"));
        }

        public static string Capture(string executable, string arguments)
        {
            try
            {
                ProcessStartInfo start = new ProcessStartInfo();
                start.FileName = executable;
                start.Arguments = arguments;
                start.UseShellExecute = false;
                start.CreateNoWindow = true;
                start.RedirectStandardOutput = true;
                start.RedirectStandardError = true;
                using (Process process = Process.Start(start))
                {
                    string output = process.StandardOutput.ReadToEnd();
                    process.WaitForExit();
                    return process.ExitCode == 0 ? output.Trim() : string.Empty;
                }
            }
            catch
            {
                return string.Empty;
            }
        }

        public static string Quote(string value)
        {
            StringBuilder quoted = new StringBuilder();
            quoted.Append('"');
            int backslashes = 0;
            foreach (char character in value)
            {
                if (character == '\\')
                {
                    backslashes++;
                    continue;
                }
                if (character == '"')
                {
                    quoted.Append('\\', backslashes * 2 + 1);
                    quoted.Append('"');
                    backslashes = 0;
                    continue;
                }
                quoted.Append('\\', backslashes);
                backslashes = 0;
                quoted.Append(character);
            }
            quoted.Append('\\', backslashes * 2);
            quoted.Append('"');
            return quoted.ToString();
        }

        public static CommandResult CreateProject(ProjectRequest request)
        {
            string python = FindPython();
            string script = FindNewProjectScript();
            if (python == null)
                throw new InvalidOperationException("Python 3 non trovato nel PATH.");
            if (script == null)
                throw new InvalidOperationException("new_project.py non trovato. Reinstallare pcb-design-system.");

            List<string> arguments = new List<string>();
            arguments.Add(Quote(script));
            arguments.Add(Quote(request.Name));
            arguments.Add("--target");
            arguments.Add(Quote(request.Target));
            arguments.Add("--repo");
            arguments.Add(Quote(request.Repository));
            arguments.Add("--git-name");
            arguments.Add(Quote(request.GitName));
            arguments.Add("--git-email");
            arguments.Add(Quote(request.GitEmail));
            arguments.Add(request.Public ? "--public" : "--private");
            if (!request.CreateGitHub)
                arguments.Add("--no-github");

            ProcessStartInfo start = new ProcessStartInfo();
            start.FileName = python;
            start.Arguments = string.Join(" ", arguments.ToArray());
            start.UseShellExecute = false;
            start.CreateNoWindow = true;
            start.RedirectStandardOutput = true;
            start.RedirectStandardError = true;
            start.StandardOutputEncoding = Encoding.UTF8;
            start.StandardErrorEncoding = Encoding.UTF8;

            using (Process process = Process.Start(start))
            {
                string stdout = process.StandardOutput.ReadToEnd();
                string stderr = process.StandardError.ReadToEnd();
                process.WaitForExit();
                return new CommandResult
                {
                    ExitCode = process.ExitCode,
                    Output = (stdout + Environment.NewLine + stderr).Trim()
                };
            }
        }

        public static void OpenAgent(string agent, string target)
        {
            if (agent.StartsWith("ChatGPT", StringComparison.OrdinalIgnoreCase))
            {
                string uri = "codex://threads/new?path=" + Uri.EscapeDataString(target);
                Process.Start(new ProcessStartInfo(uri) { UseShellExecute = true });
                return;
            }

            string antigravity = FindAntigravity();
            if (antigravity == null)
                throw new InvalidOperationException("Antigravity non trovato.");
            ProcessStartInfo start = new ProcessStartInfo();
            start.FileName = antigravity;
            start.Arguments = Quote(target);
            start.WorkingDirectory = target;
            start.UseShellExecute = true;
            Process.Start(start);
        }

        public static string[] Diagnostics()
        {
            string home = Environment.GetFolderPath(Environment.SpecialFolder.UserProfile);
            string gh = FindExecutable("gh.exe", Path.Combine(
                Environment.GetFolderPath(Environment.SpecialFolder.ProgramFiles),
                "GitHub CLI", "gh.exe"));
            string git = FindExecutable("git.exe");
            string target = Path.Combine(home, "pcb-launcher-test");
            return new[]
            {
                "PCB Project Launcher diagnostics",
                "NewProjectScript=" + (FindNewProjectScript() ?? "NOT FOUND"),
                "Python=" + (FindPython() ?? "NOT FOUND"),
                "Git=" + (git ?? "NOT FOUND"),
                "GitHubCLI=" + (gh ?? "NOT FOUND"),
                "Antigravity=" + (FindAntigravity() ?? "NOT FOUND"),
                "CodexUri=codex://threads/new?path=" + Uri.EscapeDataString(target),
                "SlugTest=" + Slugify("Progetto PCB di prova")
            };
        }
    }

    internal sealed class LauncherForm : Form
    {
        private readonly ComboBox agentBox = new ComboBox();
        private readonly TextBox nameBox = new TextBox();
        private readonly TextBox repositoryBox = new TextBox();
        private readonly TextBox targetBox = new TextBox();
        private readonly ComboBox visibilityBox = new ComboBox();
        private readonly TextBox gitNameBox = new TextBox();
        private readonly TextBox gitEmailBox = new TextBox();
        private readonly CheckBox githubBox = new CheckBox();
        private readonly CheckBox openBox = new CheckBox();
        private readonly Button createButton = new Button();
        private readonly TextBox logBox = new TextBox();
        private bool updating;
        private bool repositoryEdited;
        private bool targetEdited;

        public LauncherForm()
        {
            Text = "PCB Design System - Nuovo progetto";
            try
            {
                Icon = System.Drawing.Icon.ExtractAssociatedIcon(Application.ExecutablePath);
            }
            catch
            {
            }
            StartPosition = FormStartPosition.CenterScreen;
            MinimumSize = new Size(760, 650);
            Size = new Size(820, 700);
            Font = new Font("Segoe UI", 9F);

            TableLayoutPanel layout = new TableLayoutPanel();
            layout.Dock = DockStyle.Fill;
            layout.Padding = new Padding(18);
            layout.ColumnCount = 3;
            layout.RowCount = 12;
            layout.ColumnStyles.Add(new ColumnStyle(SizeType.Absolute, 165F));
            layout.ColumnStyles.Add(new ColumnStyle(SizeType.Percent, 100F));
            layout.ColumnStyles.Add(new ColumnStyle(SizeType.Absolute, 100F));
            Controls.Add(layout);

            Label title = new Label();
            title.Text = "Crea un progetto PCB tracciabile";
            title.Font = new Font(Font, FontStyle.Bold);
            title.AutoSize = true;
            title.Margin = new Padding(0, 0, 0, 12);
            layout.Controls.Add(title, 0, 0);
            layout.SetColumnSpan(title, 3);

            ConfigureDropDown(agentBox, new[] { "ChatGPT / Codex", "Gemini / Antigravity" }, 0);
            AddRow(layout, 1, "Ambiente AI", agentBox, null);

            nameBox.TextChanged += NameChanged;
            AddRow(layout, 2, "Nome progetto", nameBox, null);

            repositoryBox.TextChanged += RepositoryChanged;
            AddRow(layout, 3, "Repository GitHub", repositoryBox, null);

            targetBox.TextChanged += delegate { if (!updating) targetEdited = true; };
            Button browseButton = new Button();
            browseButton.Text = "Sfoglia...";
            browseButton.Dock = DockStyle.Fill;
            browseButton.Click += BrowseClicked;
            AddRow(layout, 4, "Cartella repository", targetBox, browseButton);

            ConfigureDropDown(visibilityBox, new[] { "Privato", "Pubblico" }, 0);
            AddRow(layout, 5, "Visibilità", visibilityBox, null);

            gitNameBox.Text = LauncherSupport.Capture("git", "config --global --get user.name");
            AddRow(layout, 6, "Autore Git", gitNameBox, null);

            gitEmailBox.Text = LauncherSupport.Capture("git", "config --global --get user.email");
            AddRow(layout, 7, "Email Git", gitEmailBox, null);

            FlowLayoutPanel options = new FlowLayoutPanel();
            options.Dock = DockStyle.Fill;
            options.AutoSize = true;
            githubBox.Text = "Crea e pubblica su GitHub";
            githubBox.Checked = true;
            githubBox.AutoSize = true;
            openBox.Text = "Apri nell’ambiente scelto";
            openBox.Checked = true;
            openBox.AutoSize = true;
            options.Controls.Add(githubBox);
            options.Controls.Add(openBox);
            layout.Controls.Add(options, 1, 8);
            layout.SetColumnSpan(options, 2);

            createButton.Text = "Crea progetto";
            createButton.Height = 38;
            createButton.Dock = DockStyle.Fill;
            createButton.Click += CreateClicked;
            layout.Controls.Add(createButton, 1, 9);
            layout.SetColumnSpan(createButton, 2);

            Label note = new Label();
            note.Text = "Viene creato un repository indipendente con documentazione, strumenti di controllo e primo commit.";
            note.AutoSize = true;
            note.ForeColor = Color.DimGray;
            note.Margin = new Padding(0, 8, 0, 8);
            layout.Controls.Add(note, 1, 10);
            layout.SetColumnSpan(note, 2);

            logBox.Multiline = true;
            logBox.ReadOnly = true;
            logBox.ScrollBars = ScrollBars.Vertical;
            logBox.Dock = DockStyle.Fill;
            logBox.BackColor = Color.White;
            layout.Controls.Add(logBox, 0, 11);
            layout.SetColumnSpan(logBox, 3);
            layout.RowStyles.Add(new RowStyle(SizeType.AutoSize));
            for (int i = 1; i <= 10; i++)
                layout.RowStyles.Add(new RowStyle(SizeType.AutoSize));
            layout.RowStyles.Add(new RowStyle(SizeType.Percent, 100F));

            updating = true;
            repositoryBox.Text = "nuovo-progetto-pcb";
            targetBox.Text = Path.Combine(
                Environment.GetFolderPath(Environment.SpecialFolder.MyDocuments),
                "PCB Projects", repositoryBox.Text);
            updating = false;
        }

        private static void ConfigureDropDown(ComboBox box, string[] items, int selected)
        {
            box.DropDownStyle = ComboBoxStyle.DropDownList;
            box.Dock = DockStyle.Fill;
            box.Items.AddRange(items);
            box.SelectedIndex = selected;
        }

        private static void AddRow(TableLayoutPanel layout, int row, string labelText, Control main, Control trailing)
        {
            Label label = new Label();
            label.Text = labelText;
            label.AutoSize = true;
            label.Anchor = AnchorStyles.Left;
            label.Margin = new Padding(0, 8, 8, 8);
            main.Dock = DockStyle.Fill;
            main.Margin = new Padding(0, 4, 8, 4);
            layout.Controls.Add(label, 0, row);
            layout.Controls.Add(main, 1, row);
            if (trailing == null)
                layout.SetColumnSpan(main, 2);
            else
                layout.Controls.Add(trailing, 2, row);
        }

        private void NameChanged(object sender, EventArgs e)
        {
            if (updating || repositoryEdited)
                return;
            string slug = LauncherSupport.Slugify(nameBox.Text);
            updating = true;
            repositoryBox.Text = slug;
            if (!targetEdited)
            {
                string parent = Path.GetDirectoryName(targetBox.Text);
                if (!string.IsNullOrWhiteSpace(parent) && !string.IsNullOrWhiteSpace(slug))
                    targetBox.Text = Path.Combine(parent, slug);
            }
            updating = false;
        }

        private void RepositoryChanged(object sender, EventArgs e)
        {
            if (updating)
                return;
            repositoryEdited = true;
            if (!targetEdited)
            {
                string parent = Path.GetDirectoryName(targetBox.Text);
                if (!string.IsNullOrWhiteSpace(parent) && !string.IsNullOrWhiteSpace(repositoryBox.Text))
                {
                    updating = true;
                    targetBox.Text = Path.Combine(parent, repositoryBox.Text);
                    updating = false;
                }
            }
        }

        private void BrowseClicked(object sender, EventArgs e)
        {
            using (FolderBrowserDialog dialog = new FolderBrowserDialog())
            {
                dialog.Description = "Scegli la cartella che conterrà il nuovo repository";
                dialog.ShowNewFolderButton = true;
                string currentParent = Path.GetDirectoryName(targetBox.Text);
                if (!string.IsNullOrWhiteSpace(currentParent) && Directory.Exists(currentParent))
                    dialog.SelectedPath = currentParent;
                if (dialog.ShowDialog(this) == DialogResult.OK)
                {
                    string folderName = string.IsNullOrWhiteSpace(repositoryBox.Text)
                        ? "nuovo-progetto-pcb"
                        : repositoryBox.Text.Trim();
                    targetBox.Text = Path.Combine(dialog.SelectedPath, folderName);
                    targetEdited = true;
                }
            }
        }

        private string ValidateInput()
        {
            if (string.IsNullOrWhiteSpace(nameBox.Text))
                return "Inserire il nome del progetto.";
            if (!Regex.IsMatch(repositoryBox.Text.Trim(), @"^[A-Za-z0-9._-]+$"))
                return "Il nome del repository può contenere solo lettere, numeri, punto, trattino e underscore.";
            if (string.IsNullOrWhiteSpace(targetBox.Text))
                return "Scegliere la cartella del repository.";
            if (string.IsNullOrWhiteSpace(gitNameBox.Text))
                return "Inserire il nome dell’autore Git.";
            if (string.IsNullOrWhiteSpace(gitEmailBox.Text) || !gitEmailBox.Text.Contains("@"))
                return "Inserire un indirizzo email Git valido.";
            return null;
        }

        private async void CreateClicked(object sender, EventArgs e)
        {
            string validation = ValidateInput();
            if (validation != null)
            {
                MessageBox.Show(this, validation, "Dati mancanti", MessageBoxButtons.OK, MessageBoxIcon.Warning);
                return;
            }

            ProjectRequest request = new ProjectRequest();
            request.Agent = agentBox.SelectedItem.ToString();
            request.Name = nameBox.Text.Trim();
            request.Repository = repositoryBox.Text.Trim();
            request.Target = Path.GetFullPath(targetBox.Text.Trim());
            request.GitName = gitNameBox.Text.Trim();
            request.GitEmail = gitEmailBox.Text.Trim();
            request.Public = visibilityBox.SelectedIndex == 1;
            request.CreateGitHub = githubBox.Checked;
            request.OpenAgent = openBox.Checked;

            createButton.Enabled = false;
            logBox.Text = "Creazione in corso..." + Environment.NewLine;
            try
            {
                CommandResult result = await Task.Run(delegate { return LauncherSupport.CreateProject(request); });
                logBox.Text = result.Output;
                if (result.ExitCode != 0)
                    throw new InvalidOperationException(string.IsNullOrWhiteSpace(result.Output)
                        ? "La creazione non è riuscita."
                        : result.Output);

                logBox.AppendText(Environment.NewLine + Environment.NewLine + "Progetto creato: " + request.Target);
                if (request.OpenAgent)
                {
                    try
                    {
                        LauncherSupport.OpenAgent(request.Agent, request.Target);
                    }
                    catch (Exception openError)
                    {
                        logBox.AppendText(Environment.NewLine + "Progetto creato, ma apertura automatica non riuscita: " + openError.Message);
                        Process.Start(new ProcessStartInfo(request.Target) { UseShellExecute = true });
                    }
                }
                MessageBox.Show(this, "Progetto creato correttamente.", "PCB Design System", MessageBoxButtons.OK, MessageBoxIcon.Information);
            }
            catch (Exception error)
            {
                logBox.AppendText(Environment.NewLine + error.Message);
                MessageBox.Show(this, error.Message, "Creazione non riuscita", MessageBoxButtons.OK, MessageBoxIcon.Error);
            }
            finally
            {
                createButton.Enabled = true;
            }
        }
    }
}
