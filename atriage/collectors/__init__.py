from atriage.collectors import afl, flatdir


collectors_index = {
    afl.AFLCollector.name: afl.AFLCollector,
    flatdir.FlatDirCollector.name: flatdir.FlatDirCollector
}
