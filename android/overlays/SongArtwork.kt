package com.ivor.ivormusic.ui.components

import android.graphics.Bitmap
import android.graphics.BitmapFactory
import android.media.MediaMetadataRetriever
import androidx.compose.foundation.Image
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.rounded.MusicNote
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.runtime.Composable
import androidx.compose.runtime.produceState
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.asImageBitmap
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.platform.LocalContext
import coil.compose.AsyncImage
import coil.request.ImageRequest
import com.ivor.ivormusic.data.Song
import com.ivor.ivormusic.data.SongSource
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import java.io.File

/**
 * Resilient album artwork: device embedded cover is a fallback layer for
 * MediaStore album-art URIs that are missing or unreadable. Stream artwork
 * remains URL-based and keeps its low-resolution image while HD loads.
 */
@Composable
fun SongArtwork(
    song: Song,
    contentDescription: String?,
    modifier: Modifier = Modifier,
    contentScale: ContentScale = ContentScale.Crop
) {
    val context = LocalContext.current
    val embedded by produceState<Bitmap?>(initialValue = null, song.filePath, song.source) {
        value = if (song.source == SongSource.LOCAL && !song.filePath.isNullOrBlank()) {
            withContext(Dispatchers.IO) { readEmbeddedCover(song.filePath) }
        } else null
    }
    val lowRes: Any? = song.thumbnailUrl ?: song.albumArtUri
    val highRes = song.highResThumbnailUrl?.takeIf { it != song.thumbnailUrl }
    Box(modifier = modifier) {
        if (embedded != null) {
            Image(
                bitmap = embedded!!.asImageBitmap(),
                contentDescription = contentDescription,
                modifier = Modifier.fillMaxSize(),
                contentScale = contentScale
            )
        } else {
            Box(
                modifier = Modifier.fillMaxSize(),
                contentAlignment = Alignment.Center
            ) {
                Icon(
                    Icons.Rounded.MusicNote,
                    contentDescription = null,
                    tint = MaterialTheme.colorScheme.onSurfaceVariant,
                    modifier = Modifier.fillMaxSize(0.35f)
                )
            }
        }
        if (lowRes != null) {
            AsyncImage(
                model = lowRes,
                contentDescription = contentDescription,
                modifier = Modifier.fillMaxSize(),
                contentScale = contentScale
            )
        }
        if (highRes != null) {
            AsyncImage(
                model = ImageRequest.Builder(context)
                    .data(highRes)
                    .crossfade(300)
                    .build(),
                contentDescription = null,
                modifier = Modifier.fillMaxSize(),
                contentScale = contentScale
            )
        }
    }
}

private fun readEmbeddedCover(path: String): Bitmap? {
    val file = File(path)
    if (!file.isFile) return null
    val retriever = MediaMetadataRetriever()
    return try {
        retriever.setDataSource(path)
        val bytes = retriever.embeddedPicture ?: return null
        BitmapFactory.decodeByteArray(bytes, 0, bytes.size)
    } catch (_: Exception) {
        null
    } finally {
        runCatching { retriever.release() }
    }
}
