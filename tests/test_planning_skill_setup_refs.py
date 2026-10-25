"""Scan portable skill assets and the complete shipped package."""
from pathlib import Path
import re
import subprocess
import pytest
ROOT = Path(__file__).resolve().parents[1]
SKILLS = (
    'dev-plan', 'strawman', 'grilling', 'grill-me', 'grill-with-docs',
    'to-spec', 'spec-review', 'to-tickets', 'domain-modeling',
    'visual-review', 'diagramming',
)


def private_label_pattern():
    # Only enumerated spec/status values are labels; prose like spec/design
    # and status/counts must remain valid. Other policy families are unambiguous.
    families = ('type', 'project', 'priority', 'llm', 'model', 'mode', 'node',
                'platform', 'dispatch', 'area', 'host', 'investigation', 'claim',
                'from', 'testdata', 'sync')
    return (r'(?<![\w/-])(?:(?:' + '|'.join(families) + r')/(?:[\w.-]+|\*)|'
            r'spec/(?:\*|tbd|rough|thorough)|'
            r'status/(?:\*|backlog|next|active|blocked|deployed|sim-pending|device-pending|visual-pending))'
            r'(?![\w/-])')


# Extend the skill-scoping inventory's name pattern with current policy labels
# and private mechanisms. Keep historical spec labels detectable as well.
SETUP = re.compile(
    private_label_pattern() + '|'
    r'corey|coreyfloyd|~/\x6fbsidian|\x2fusers/corey|~/ops/|~/\.claude/dotfiles|'
    r'\x63laude-dotfiles|\x6dini1|\x6dini2|mac mini|macbook|propeller|podcastcrawler|'
    r'quotes|\x61dmin-panel|slack|herdr|noteplan|issue-workflow|spec/(?:\*|rough\b|thorough\b|light\b|none\b)|'
    r'approval[ -]slates?|launch-evaluator\.py|gh\s+project\s+item-add\s+2\b|'
    r'publish-doc\.sh|surface[ -]gate|fleet[ -]map|rules/practices|'
    r'fleet\.css|single-launch[ -]slate|--(?:host|sess(?:ion)?|job|daemon)(?:[-\w]*)\b', re.I,
)
# Only the source attribution fields are exempt, never fork/ticket/history lines.
UPSTREAM_FIELD = re.compile(
    r'^- \*\*(?:Upstream repo|Path in upstream|Source commit|Copied|License)\*\*:'
)


def setup_references(directory):
    violations = []
    assert (directory / 'SKILL.md').is_file(), f'Missing shipped skill: {directory}'
    for path in sorted(directory.rglob('*')):
        if not path.is_file():
            continue
        for number, line in enumerate(path.read_bytes().decode('utf-8', errors='replace').splitlines(), 1):
            if path.name == 'PROVENANCE.md' and UPSTREAM_FIELD.match(line):
                continue
            if SETUP.search(line):
                # The worked messaging review names the public product, not a
                # private channel or integration. Exempt only that exact word
                # in that one example; every private identifier still counts.
                public_product_example = (
                    path.relative_to(directory).as_posix() == 'examples/channel-agents.html'
                    and directory.name == 'visual-review'
                )
                violations.extend(f'{path}:{number}: {match.group()}'
                                  for match in SETUP.finditer(line)
                                  if not (public_product_example and match.group() == 'Slack'
                                          and re.compile(r'(?<![\w/#-])Slack(?![\w/-])').match(line, match.start())))
    return violations


@pytest.mark.parametrize('skill', SKILLS)
def test_no_setup_references_in_any_shipped_file(skill):
    violations = setup_references(ROOT / 'skills' / skill)
    print(f'{skill}: setup-reference count = {len(violations)}')
    assert not violations, '\n'.join(violations)


@pytest.mark.parametrize('skill', ('grilling', 'grill-me', 'grill-with-docs', 'domain-modeling', 'to-tickets'))
def test_upstream_snapshot_credit_is_preserved(skill):
    text = (ROOT / 'skills' / skill / 'PROVENANCE.md').read_text()
    for field, value in {
        'Upstream repo': 'git@github.com:mattpocock/skills.git',
        'Path in upstream': ('skills/productivity/' if skill in ('grilling', 'grill-me') else 'skills/engineering/') + skill,
        'Source commit': '147914f7eb173499c5c2797a1363c7593fa57d0c',
        'Copied': '2026-08-16',
    }.items():
        assert f'- **{field}**: {value}' in text
    assert re.search(r'- \*\*License\*\*: MIT(?: License)?', text)
    notice = (ROOT / 'LICENSE-MIT').read_text()
    assert 'Copyright (c) 2026 Matt Pocock' in notice
    assert 'Permission is hereby granted, free of charge' in notice
    assert 'Credit for the original content belongs to the upstream author.' in text
    assert 'Fork (copied from)' not in text
    assert '**Ticket**' not in text


def test_skill_entrypoints_and_relative_links_resolve():
    for skill in SKILLS:
        directory = ROOT / 'skills' / skill
        assert f'name: {skill}\n' in (directory / 'SKILL.md').read_text()
        for path in directory.rglob('*.md'):
            prose = re.sub(r'```.*?```', '', path.read_text(), flags=re.S)
            for target in re.findall(r'\]\(([^)]+)\)', prose):
                if re.match(r'[a-z]+:|#', target):
                    continue
                target = target.split('#', 1)[0]
                assert (path.parent / target).exists(), (path, target)
    for target in ('grilling', 'domain-modeling'):
        assert (ROOT / 'skills' / target / 'SKILL.md').is_file()


def test_release_inventory_covers_all_eleven_skills():
    assert set(SKILLS) == {
        'dev-plan', 'strawman', 'grilling', 'grill-me', 'grill-with-docs',
        'to-spec', 'spec-review', 'to-tickets', 'domain-modeling',
        'visual-review', 'diagramming',
    }


@pytest.mark.parametrize('extension', ['md', 'css', 'html', 'svg', 'py', 'json'])
@pytest.mark.parametrize('mechanism', [
    'Corey', '\x6dini1', '\x61dmin-panel', 'issue-workflow', 'spec/*',
    'spec/tbd', 'spec/rough', 'spec/thorough', 'approval slates', 'approval-slate',
    'single-launch slate', 'launch-evaluator.py', 'gh project item-add 2',
    'publish-doc.sh', 'surface gate', 'surface-gate', 'fleet-map', 'fleet.css',
    '--host', '--sess-soft', '--session', '--job', '--daemon-soft',
])
def test_counter_detects_private_mechanisms_in_every_asset(tmp_path, extension, mechanism):
    (tmp_path / 'SKILL.md').write_text('Portable planning skill')
    asset = tmp_path / f'nested/asset.{extension}'
    asset.parent.mkdir()
    asset.write_text(mechanism)
    findings = setup_references(tmp_path)
    assert len(findings) == 1
    assert f'{asset}:1:' in findings[0]


def test_counter_exempts_only_upstream_provenance_fields(tmp_path):
    (tmp_path / 'SKILL.md').write_text('Portable planning skill')
    provenance = tmp_path / 'PROVENANCE.md'
    provenance.write_text('- **Upstream repo**: \x61dmin-panel\n'
                          '- **Path in upstream**: corey\n'
                          '- **Source commit**: corey\n'
                          '- **Copied**: corey\n'
                          '- **License**: corey\n'
                          'Credit for the original content belongs to the upstream author.\n')
    assert not setup_references(tmp_path)
    with provenance.open('a') as stream:
        stream.write('- **Fork (copied from)**: \x63laude-dotfiles\n'
                     '- **Ticket**: coreyfloyd/\x63laude-dotfiles/issues/1\n')
    assert len(setup_references(tmp_path)) == 3
    # A matching field outside PROVENANCE.md has no exemption.
    (tmp_path / 'asset.svg').write_text('- **Upstream repo**: \x61dmin-panel')
    assert len(setup_references(tmp_path)) == 4


def test_counter_does_not_mistake_generic_spec_design_for_a_label(tmp_path):
    (tmp_path / 'SKILL.md').write_text('Review a spec/design before approval.')
    assert not setup_references(tmp_path)












def test_channel_example_exempts_only_the_public_product_name(tmp_path):
    directory = tmp_path / 'visual-review'
    (directory / 'examples').mkdir(parents=True)
    (directory / 'SKILL.md').write_text('Portable review skill')
    example = directory / 'examples/channel-agents.html'
    example.write_text('Slack channel agents')
    assert setup_references(directory) == []
    example.write_text('Slack on \x6dini1 in \x61dmin-panel at \x2fUsers/corey Slack-routing Slack/channels')
    findings = setup_references(directory)
    assert len(findings) == 5, findings
    (directory / 'asset.html').write_text('Slack')
    assert len(setup_references(directory)) == 6

# Test fixtures spell restricted identifiers with escapes so the entire public
# history, including its negative tests, remains clean under a literal range scan.
PUBLIC_PRIVATE = re.compile(
    r'admin' + r'-panel|claude' + r'-dotfiles|obsi' + r'dian|/Use' + r'rs/|'
    r'mini' + r'1|mini' + r'2|tail' + r'scale|100\.[0-9]+\.', re.I)


def test_every_shipped_file_has_zero_private_references():
    files = [p for p in ROOT.rglob('*') if p.is_file()
             and not any(part in ('.git', '.venv', '__pycache__', '.pytest_cache')
                         for part in p.relative_to(ROOT).parts)]
    assert files
    offenders = []
    for path in sorted(files):
        matches = list(PUBLIC_PRIVATE.finditer(path.read_bytes().decode('utf-8', errors='replace')))
        print(f'{path.relative_to(ROOT)}: private-reference count = {len(matches)}')
        offenders.extend(f'{path.relative_to(ROOT)}: {m.group()}' for m in matches)
    assert not offenders, '\n'.join(offenders)
