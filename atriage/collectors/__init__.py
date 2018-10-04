from atriage.collectors import afl, flatdir


collectors_index = {
    afl.AFLCollector(None).name: afl.AFLCollector,
    flatdir.FlatDirCollector(None).name: flatdir.FlatDirCollector
}
