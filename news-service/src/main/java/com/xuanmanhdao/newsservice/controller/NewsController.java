package com.xuanmanhdao.newsservice.controller;


import com.xuanmanhdao.newsservice.entity.NewsDocumentEntity;
import com.xuanmanhdao.newsservice.service.NewsService;
import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/news")
@RequiredArgsConstructor
public class NewsController {

    private final NewsService newsService;

    @GetMapping("/all")
    public Iterable<NewsDocumentEntity> getAll() {
        return newsService.getAll();
    }

    @GetMapping("/search")
    public Page<NewsDocumentEntity> searchByTitle(
            @RequestParam String keyword,
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "10") int size
    ) {
        return newsService.searchByTitle(keyword, PageRequest.of(page, size));
    }

    @GetMapping("/source")
    public Page<NewsDocumentEntity> searchBySource(
            @RequestParam String source,
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "10") int size
    ) {
        return newsService.searchBySource(source, PageRequest.of(page, size));
    }
}
