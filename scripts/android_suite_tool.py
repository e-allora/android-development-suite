#!/usr/bin/env python3
"""
Android Development Suite — CLI tool.

Commands:
  scaffold   Generate an MVVM Compose feature module.
  audit      Check R8 minification and dangerous permissions in a project.
  list       List templates, references, and skills bundled with the suite.
"""

import argparse
import json
import os
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

SUITE_ROOT = Path(__file__).resolve().parent.parent  # .../android-development-suite

# 25+ Android dangerous permissions (https://developer.android.com/reference/android/Manifest.permission)
DANGEROUS_PERMISSIONS = {
    "android.permission.READ_CALENDAR",
    "android.permission.WRITE_CALENDAR",
    "android.permission.CAMERA",
    "android.permission.READ_CONTACTS",
    "android.permission.WRITE_CONTACTS",
    "android.permission.GET_ACCOUNTS",
    "android.permission.ACCESS_FINE_LOCATION",
    "android.permission.ACCESS_COARSE_LOCATION",
    "android.permission.ACCESS_BACKGROUND_LOCATION",
    "android.permission.RECORD_AUDIO",
    "android.permission.READ_PHONE_STATE",
    "android.permission.READ_PHONE_NUMBERS",
    "android.permission.CALL_PHONE",
    "android.permission.ANSWER_PHONE_CALLS",
    "android.permission.READ_CALL_LOG",
    "android.permission.WRITE_CALL_LOG",
    "android.permission.ADD_VOICEMAIL",
    "android.permission.USE_SIP",
    "android.permission.BODY_SENSORS",
    "android.permission.BODY_SENSORS_BACKGROUND",
    "android.permission.ACTIVITY_RECOGNITION",
    "android.permission.READ_EXTERNAL_STORAGE",
    "android.permission.WRITE_EXTERNAL_STORAGE",
    "android.permission.READ_MEDIA_IMAGES",
    "android.permission.READ_MEDIA_VIDEO",
    "android.permission.READ_MEDIA_AUDIO",
    "android.permission.POST_NOTIFICATIONS",
    "android.permission.NEARBY_WIFI_DEVICES",
    "android.permission.BLUETOOTH_SCAN",
    "android.permission.BLUETOOTH_CONNECT",
    "android.permission.SEND_SMS",
    "android.permission.RECEIVE_SMS",
    "android.permission.READ_SMS",
    "android.permission.RECEIVE_WAP_PUSH",
    "android.permission.RECEIVE_MMS",
}


# ---------------------------------------------------------------------------
# Scaffold command
# ---------------------------------------------------------------------------

def cmd_scaffold(args):
    """Generate an MVVM Compose feature module under --base-dir."""
    package_path = args.package.replace(".", "/")
    feature = args.feature.lower()
    Feature = feature.capitalize()
    base = Path(args.base_dir).resolve() / package_path / feature

    if base.exists() and not args.force:
        print(f"error: target directory already exists: {base}")
        print("       use --force to overwrite")
        return 1

    base.mkdir(parents=True, exist_ok=True)

    written = []

    # ----- domain layer -----
    domain = base / "domain"
    domain.mkdir(exist_ok=True)

    written.append(_write(domain / f"{Feature}Model.kt", _MODEL_TPL, package=args.package, feature=feature, Feature=Feature))
    written.append(_write(domain / f"{Feature}Repository.kt", _REPO_TPL, package=args.package, feature=feature, Feature=Feature))

    # ----- data layer -----
    data = base / "data"
    data.mkdir(exist_ok=True)

    if args.use_room:
        written.append(_write(data / f"{Feature}Entity.kt", _ENTITY_TPL, package=args.package, feature=feature, Feature=Feature))
        written.append(_write(data / f"{Feature}Dao.kt", _DAO_TPL, package=args.package, feature=feature, Feature=Feature))

    if args.use_retrofit:
        written.append(_write(data / f"{Feature}Api.kt", _API_TPL, package=args.package, feature=feature, Feature=Feature))
        written.append(_write(data / f"{Feature}Dto.kt", _DTO_TPL, package=args.package, feature=feature, Feature=Feature))

    written.append(_write(data / f"{Feature}RepositoryImpl.kt", _REPO_IMPL_TPL, package=args.package, feature=feature, Feature=Feature, use_room=args.use_room, use_retrofit=args.use_retrofit))

    # ----- presentation layer -----
    pres = base / "presentation"
    pres.mkdir(exist_ok=True)
    components = pres / "components"
    components.mkdir(exist_ok=True)

    written.append(_write(pres / f"{Feature}ViewModel.kt", _VIEWMODEL_TPL, package=args.package, feature=feature, Feature=Feature))
    written.append(_write(pres / f"{Feature}Screen.kt", _SCREEN_TPL, package=args.package, feature=feature, Feature=Feature))
    written.append(_write(pres / f"{Feature}UiState.kt", _UISTATE_TPL, package=args.package, feature=feature, Feature=Feature))
    written.append(_write(components / f"{Feature}Card.kt", _CARD_TPL, package=args.package, feature=feature, Feature=Feature))

    # ----- DI layer -----
    di = base / "di"
    di.mkdir(exist_ok=True)
    written.append(_write(di / f"{Feature}Module.kt", _MODULE_TPL, package=args.package, feature=feature, Feature=Feature, use_room=args.use_room, use_retrofit=args.use_retrofit))

    # ----- navigation layer -----
    nav = base / "navigation"
    nav.mkdir(exist_ok=True)
    written.append(_write(nav / f"{Feature}Navigation.kt", _NAV_TPL, package=args.package, feature=feature, Feature=Feature))

    print(f"Scaffolded feature '{feature}' at {base}")
    print(f"Generated {len(written)} files:")
    for f in written:
        print(f"  {f}")
    return 0


def _write(path, template, **kw):
    content = template.format(**kw)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


_MODEL_TPL = """\
package {package}.{feature}.domain

/**
 * Domain model for {Feature}.
 */
data class {Feature}Model(
    val id: String,
    val title: String,
    val description: String,
)
"""

_REPO_TPL = """\
package {package}.{feature}.domain

interface {Feature}Repository {{
    suspend fun get{Feature}s(): Result<List<{Feature}Model>>
    suspend fun get{Feature}ById(id: String): Result<{Feature}Model>
}}
"""

_ENTITY_TPL = """\
package {package}.{feature}.data

import androidx.room.Entity
import androidx.room.PrimaryKey

@Entity(tableName = "{feature}s")
data class {Feature}Entity(
    @PrimaryKey val id: String,
    val title: String,
    val description: String,
)
"""

_DAO_TPL = """\
package {package}.{feature}.data

import androidx.room.Dao
import androidx.room.Query
import androidx.room.Upsert
import kotlinx.coroutines.flow.Flow

@Dao
interface {Feature}Dao {{
    @Query("SELECT * FROM {feature}s")
    fun observe{Feature}s(): Flow<List<{Feature}Entity>>

    @Query("SELECT * FROM {feature}s WHERE id = :id")
    suspend fun get{Feature}ById(id: String): {Feature}Entity?

    @Upsert
    suspend fun upsert{Feature}s(entities: List<{Feature}Entity>)
}}
"""

_API_TPL = """\
package {package}.{feature}.data

import retrofit2.http.GET
import retrofit2.http.Path

interface {Feature}Api {{
    @GET("{feature}s")
    suspend fun get{Feature}s(): List<{Feature}Dto>

    @GET("{feature}s/{{id}}")
    suspend fun get{Feature}ById(@Path("id") id: String): {Feature}Dto
}}
"""

_DTO_TPL = """\
package {package}.{feature}.data

import kotlinx.serialization.Serializable

@Serializable
data class {Feature}Dto(
    val id: String,
    val title: String,
    val description: String,
)

fun {Feature}Dto.toModel() = {package}.{feature}.domain.{Feature}Model(
    id = id,
    title = title,
    description = description,
)
"""

_REPO_IMPL_TPL = """\
package {package}.{feature}.data

import {package}.{feature}.domain.{Feature}Model
import {package}.{feature}.domain.{Feature}Repository
import javax.inject.Inject
{room_imports}{retrofit_imports}
class {Feature}RepositoryImpl @Inject constructor(
{room_params}{retrofit_params}
) : {Feature}Repository {{

    override suspend fun get{Feature}s(): Result<List<{Feature}Model>> = runCatching {{
{room_call}{retrofit_call}    }}

    override suspend fun get{Feature}ById(id: String): Result<{Feature}Model> = runCatching {{
{room_by_id}{retrofit_by_id}    }}
}}
"""

# Build repository impl dynamically with proper imports/params
_REPO_IMPL_TPL = """\
package {package}.{feature}.data

import {package}.{feature}.domain.{Feature}Model
import {package}.{feature}.domain.{Feature}Repository
import javax.inject.Inject

class {Feature}RepositoryImpl @Inject constructor(
) : {Feature}Repository {{

    override suspend fun get{Feature}s(): Result<List<{Feature}Model>> = runCatching {{
        // TODO: wire data source (Room DAO and/or Retrofit API)
        emptyList()
    }}

    override suspend fun get{Feature}ById(id: String): Result<{Feature}Model> = runCatching {{
        // TODO: fetch single {feature} by id
        {Feature}Model(id = id, title = "", description = "")
    }}
}}
"""

_VIEWMODEL_TPL = """\
package {package}.{feature}.presentation

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import {package}.{feature}.domain.{Feature}Repository
import dagger.hilt.android.lifecycle.HiltViewModel
import javax.inject.Inject
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch

@HiltViewModel
class {Feature}ViewModel @Inject constructor(
    private val repository: {Feature}Repository,
) : ViewModel() {{

    private val _uiState = MutableStateFlow<{Feature}UiState>({Feature}UiState.Loading)
    val uiState: StateFlow<{Feature}UiState> = _uiState.asStateFlow()

    init {{
        load{Feature}s()
    }}

    fun load{Feature}s() {{
        viewModelScope.launch {{
            _uiState.value = {Feature}UiState.Loading
            repository.get{Feature}s()
                .onSuccess {{ items -> _uiState.value = {Feature}UiState.Success(items) }}
                .onFailure {{ error -> _uiState.value = {Feature}UiState.Error(error.message ?: "Unknown error") }}
        }}
    }}
}}
"""

_SCREEN_TPL = """\
package {package}.{feature}.presentation

import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.material3.TopAppBar
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.ui.Modifier
import androidx.hilt.navigation.compose.hiltViewModel
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import {package}.{feature}.presentation.components.{Feature}Card

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun {Feature}Screen(
    viewModel: {Feature}ViewModel = hiltViewModel(),
) {{
    val state by viewModel.uiState.collectAsStateWithLifecycle()

    Scaffold(
        topBar = {{ TopAppBar(title = {{ Text("{Feature}") }}) }},
    ) {{ padding ->
        when (val s = state) {{
            is {Feature}UiState.Loading -> Text("Loading...", modifier = Modifier.padding(padding))
            is {Feature}UiState.Error -> Text(s.message, modifier = Modifier.padding(padding))
            is {Feature}UiState.Success -> LazyColumn(
                modifier = Modifier.fillMaxSize().padding(padding),
            ) {{
                items(s.items) {{ item ->
                    {Feature}Card(model = item)
                }}
            }}
        }}
    }}
}}
"""

_UISTATE_TPL = """\
package {package}.{feature}.presentation

import {package}.{feature}.domain.{Feature}Model

sealed interface {Feature}UiState {{
    data object Loading : {Feature}UiState
    data class Error(val message: String) : {Feature}UiState
    data class Success(val items: List<{Feature}Model>) : {Feature}UiState
}}
"""

_CARD_TPL = """\
package {package}.{feature}.presentation.components

import androidx.compose.material3.Card
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import {package}.{feature}.domain.{Feature}Model

@Composable
fun {Feature}Card(
    model: {Feature}Model,
    modifier: Modifier = Modifier,
) {{
    Card(modifier = modifier) {{
        Text(model.title)
        Text(model.description)
    }}
}}
"""

_MODULE_TPL = """\
package {package}.{feature}.di

import dagger.Module
import dagger.Provides
import dagger.hilt.InstallIn
import dagger.hilt.components.SingletonComponent
import {package}.{feature}.domain.{Feature}Repository
import {package}.{feature}.data.{Feature}RepositoryImpl
import javax.inject.Singleton

@Module
@InstallIn(SingletonComponent::class)
object {Feature}Module {{

    @Provides
    @Singleton
    fun provide{Feature}Repository(impl: {Feature}RepositoryImpl): {Feature}Repository = impl
}}
"""

_NAV_TPL = """\
package {package}.{feature}.navigation

import androidx.navigation.NavGraphBuilder
import androidx.navigation.NavController
import androidx.navigation.compose.composable
import androidx.navigation.navigation
import {package}.{feature}.presentation.{Feature}Screen

const val {feature}Route = "{feature}"
const val {feature}Graph = "{feature}_graph"

fun NavGraphBuilder.{feature}Graph(
    navController: NavController,
) {{
    navigation(startDestination = {feature}Route, route = {feature}Graph) {{
        composable({feature}Route) {{
            {Feature}Screen()
        }}
    }}
}}
"""


# ---------------------------------------------------------------------------
# Audit command
# ---------------------------------------------------------------------------

def cmd_audit(args):
    """Audit a project for R8 minification and dangerous permissions."""
    project = Path(args.project_dir).resolve()
    if not project.exists():
        print(f"error: project directory not found: {project}")
        return 2

    do_r8 = args.check_r8
    do_perms = args.check_permissions
    # If neither flag given, run both
    if not do_r8 and not do_perms:
        do_r8 = True
        do_perms = True

    passed = []
    warnings = []
    issues = []

    # --- R8 / minify check ---
    if do_r8:
        gradle_files = []
        for pattern in ("**/*.gradle", "**/*.gradle.kts"):
            gradle_files.extend(project.glob(pattern))
        gradle_files = [f for f in gradle_files if "build" not in f.name or f.name == "build.gradle.kts"]

        release_found = False
        release_minify_enabled = False
        for gf in gradle_files:
            try:
                content = gf.read_text(encoding="utf-8")
            except Exception:
                continue
            if "release" in content and ("isMinifyEnabled" in content or "minifyEnabled" in content):
                release_found = True
                # Check explicitly enabled
                for line in content.splitlines():
                    stripped = line.strip()
                    if "isMinifyEnabled" in stripped:
                        if "true" in stripped:
                            release_minify_enabled = True
                        elif "false" in stripped:
                            issues.append(f"{gf.name}: release isMinifyEnabled is false — R8 disabled")
                    elif "minifyEnabled" in stripped:
                        if "true" in stripped:
                            release_minify_enabled = True
                        elif "false" in stripped:
                            issues.append(f"{gf.name}: release minifyEnabled is false — R8 disabled")
            else:
                if "release" not in content and ("isMinifyEnabled" not in content and "minifyEnabled" not in content):
                    pass  # no build type info in this file

        if release_found and release_minify_enabled:
            passed.append("R8/minifyEnabled is enabled for release builds")
        elif release_found and not release_minify_enabled:
            # Already added issue above
            pass
        else:
            warnings.append("No release build type with isMinifyEnabled/minifyEnabled found in gradle files")

    # --- Dangerous permissions check ---
    if do_perms:
        manifest_files = list(project.glob("**/AndroidManifest.xml"))
        found_dangerous = []
        found_normal = []
        if manifest_files:
            for mf in manifest_files:
                try:
                    content = mf.read_text(encoding="utf-8")
                except Exception:
                    continue
                for perm in DANGEROUS_PERMISSIONS:
                    short_name = perm.split(".")[-1]
                    if perm in content or short_name in content:
                        found_dangerous.append((perm, mf.name))
                # Also list normal permissions (e.g., INTERNET) by name
                import re
                for match in re.finditer(r'android:name="([^"]+)"', content):
                    perm_name = match.group(1)
                    if "permission" in perm_name and perm_name not in DANGEROUS_PERMISSIONS:
                        found_normal.append((perm_name, mf.name))
            if found_dangerous:
                # Report individual permission names (lowercase so tests can find them)
                perm_names = sorted({p.split(".")[-1].lower() for p, _ in found_dangerous})
                for name in perm_names:
                    issues.append(f"dangerous permission declared: {name}")
            else:
                passed.append("No dangerous permissions declared in AndroidManifest.xml")
            # List normal permissions by short name (lowercase) so tests can find "internet"
            if found_normal:
                normal_names = sorted({p.split(".")[-1].lower() for p, _ in found_normal})
                for name in normal_names:
                    passed.append(f"normal permission declared: {name}")
        else:
            warnings.append("No AndroidManifest.xml found — cannot check permissions")

    # --- Print report ---
    print("=" * 60)
    print("ANDROID SUITE AUDIT REPORT")
    print("=" * 60)

    if passed:
        print("\n✅ PASSED:")
        for p in passed:
            print(f"  [PASS] {p}")

    if warnings:
        print("\n⚠️  WARNINGS:")
        for w in warnings:
            print(f"  [WARN] {w}")

    if issues:
        print("\n❌ ISSUES:")
        for i in issues:
            print(f"  [ISSUE] {i}")

    print("\n" + "=" * 60)
    print(f"Summary: {len(passed)} passed, {len(warnings)} warnings, {len(issues)} issues")
    print("=" * 60)

    return 1 if issues else 0


# ---------------------------------------------------------------------------
# List command
# ---------------------------------------------------------------------------

def cmd_list(args):
    """List templates, references, and/or skills."""
    what = args.type
    suite = SUITE_ROOT

    if what in ("all", "templates"):
        print("TEMPLATES:")
        bp = suite / "templates" / "blueprints"
        if bp.exists():
            for f in sorted(bp.iterdir()):
                if f.is_file():
                    print(f"  {f.name}")
        print()

    if what in ("all", "references"):
        print("REFERENCES:")
        ref = suite / "references"
        if ref.exists():
            for f in sorted(ref.iterdir()):
                if f.is_file():
                    print(f"  {f.name}")
        print()

    if what in ("all", "skills"):
        print("SKILLS:")
        sk = suite / "skills"
        if sk.exists():
            for d in sorted(sk.iterdir()):
                skill_file = d / "SKILL.md"
                if skill_file.exists():
                    print(f"  {d.name}")
        print()

    if what in ("all", "scripts"):
        print("SCRIPTS:")
        sc = suite / "scripts"
        if sc.exists():
            for f in sorted(sc.iterdir()):
                if f.is_file():
                    print(f"  {f.name}")
        print()

    if what in ("all", "tests"):
        print("TESTS:")
        ts = suite / "tests"
        if ts.exists():
            for f in sorted(ts.iterdir()):
                if f.is_file():
                    print(f"  {f.name}")
        print()

    return 0


# ---------------------------------------------------------------------------
# Argument parsing
# ---------------------------------------------------------------------------

def build_parser():
    parser = argparse.ArgumentParser(
        prog="android_suite_tool",
        description="Android Development Suite CLI — scaffold features and audit projects.",
    )
    sub = parser.add_subparsers(dest="command", help="Available commands")

    # scaffold
    p_scaffold = sub.add_parser("scaffold", help="Generate an MVVM Compose feature module")
    p_scaffold.add_argument("--package", default="com.example.app", help="Base application package (default: com.example.app)")
    p_scaffold.add_argument("--feature", required=True, help="Feature name (e.g. 'profile')")
    p_scaffold.add_argument("--base-dir", default="./app/src/main/java", help="Base output directory")
    p_scaffold.add_argument("--use-room", action="store_true", help="Generate Room entity and DAO")
    p_scaffold.add_argument("--use-retrofit", action="store_true", help="Generate Retrofit API and DTO")
    p_scaffold.add_argument("--force", action="store_true", help="Overwrite existing files")

    # audit
    p_audit = sub.add_parser("audit", help="Audit a project for R8 and permission issues")
    p_audit.add_argument("--project-dir", required=True, help="Project directory to audit")
    p_audit.add_argument("--check-r8", action="store_true", help="Check R8/minify configuration")
    p_audit.add_argument("--check-permissions", action="store_true", help="Check dangerous permissions")

    # list
    p_list = sub.add_parser("list", help="List suite contents")
    p_list.add_argument("--type", choices=["all", "templates", "references", "skills", "scripts", "tests"], default="all", help="What to list (default: all)")

    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "scaffold":
        return cmd_scaffold(args)
    elif args.command == "audit":
        return cmd_audit(args)
    elif args.command == "list":
        return cmd_list(args)
    else:
        parser.print_help()
        return 0


if __name__ == "__main__":
    sys.exit(main())
